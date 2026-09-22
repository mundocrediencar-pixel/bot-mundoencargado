"""
Bot de WhatsApp para Mundo Encargado.

Flujo:
1. El cliente pregunta por un producto.
2. El bot busca en Mercado Libre (hasta 3 opciones, locales y
   priorizando Capital Federal).
3. Si hay más de una opción, el cliente elige el número.
4. El bot calcula el precio (costo + flete + 35%) y las cuotas,
   y responde con la foto y los montos.

Además, el bot reconoce dos consultas frecuentes que no son búsqueda
de producto:
- Requisitos del crédito personal para comprar un producto.
- Crédito en efectivo (se deriva a la línea de Credit Encar).
"""

import os
from flask import Flask, request, jsonify

from intent import (
    es_consulta_credito_efectivo,
    es_consulta_requisitos,
    es_saludo_o_generico,
)
from mercadolibre import buscar_productos
from pricing import calcular_precios, formatear_precio
from whatsapp import enviar_texto, enviar_imagen

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "mundoencargado")

# Número de contacto de Credit Encar, para consultas de crédito en
# efectivo (que no tienen que ver con la compra de un producto).
TELEFONO_CREDITO_EFECTIVO = "11 5182-1377"

MENSAJE_REQUISITOS = (
    "Para acceder a un producto con crédito personal, los requisitos son:\n\n"
    "1. Foto del DNI, frente y dorso.\n"
    "2. Los dos últimos recibos de sueldo.\n"
    "3. Si no tenés vivienda propia, un servicio a tu nombre del "
    "domicilio particular donde vivís.\n\n"
    "¿Querés que te ayude a buscar un producto?"
)

MENSAJE_CREDITO_EFECTIVO = (
    "Para crédito en efectivo te atienden por otra línea, la de "
    f"Credit Encar. Comunicate al {TELEFONO_CREDITO_EFECTIVO} y te "
    "asesoran directamente."
)

# Estado simple en memoria: para cada número de cliente, guardamos
# las opciones de producto que le mostramos (hasta que elija una).
# NOTA: esto se reinicia si el servidor se reinicia. Para producción
# más adelante conviene pasar esto a una base de datos.
sesiones = {}


def mensaje_precio(producto: dict) -> str:
    precios = calcular_precios(producto["precio"])
    return (
        f"*{producto['titulo']}*\n\n"
        f"Precio contado: {formatear_precio(precios['promo_encargado'])}\n"
        f"Precio de lista: {formatear_precio(precios['precio_lista'])}\n\n"
        f"O con crédito personal de la empresa en:\n"
        f"6 cuotas fijas de {formatear_precio(precios['cuota_6'])}\n"
        f"9 cuotas fijas de {formatear_precio(precios['cuota_9'])}\n"
        f"12 cuotas fijas de {formatear_precio(precios['cuota_12'])}"
    )


@app.route("/webhook", methods=["GET"])
def verificar_webhook():
    """Meta llama a este endpoint una vez, al configurar el webhook."""
    modo = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    desafio = request.args.get("hub.challenge")

    if modo == "subscribe" and token == VERIFY_TOKEN:
        return desafio, 200
    return "Token inválido", 403


@app.route("/webhook", methods=["POST"])
def recibir_mensaje():
    """Meta llama a este endpoint cada vez que llega un mensaje."""
    data = request.get_json(silent=True) or {}

    try:
        entry = data["entry"][0]
        cambios = entry["changes"][0]["value"]
        mensajes = cambios.get("messages")
        if not mensajes:
            return jsonify(status="sin mensajes"), 200

        mensaje = mensajes[0]
        numero = mensaje["from"]
        texto = mensaje.get("text", {}).get("body", "").strip()

        procesar_mensaje(numero, texto)
    except (KeyError, IndexError):
        pass

    return jsonify(status="ok"), 200


def procesar_mensaje(numero: str, texto: str) -> None:
    # Si el cliente responde con un número, está eligiendo entre las
    # opciones que le mostramos antes.
    if texto.isdigit() and numero in sesiones:
        opciones = sesiones[numero]
        indice = int(texto) - 1

        if 0 <= indice < len(opciones):
            producto = opciones[indice]
            enviar_imagen(numero, producto["imagen"], caption=producto["titulo"])
            enviar_texto(numero, mensaje_precio(producto))
            del sesiones[numero]
        else:
            enviar_texto(numero, "No encontré esa opción. Decime el número correcto (1, 2 o 3).")
        return

    # Si pregunta por crédito EN EFECTIVO, lo derivamos a la línea de
    # Credit Encar (no es una consulta de producto).
    if es_consulta_credito_efectivo(texto):
        enviar_texto(numero, MENSAJE_CREDITO_EFECTIVO)
        return

    # Si pregunta por los requisitos del crédito personal para
    # comprar un producto, le mandamos la lista de documentación.
    if es_consulta_requisitos(texto):
        enviar_texto(numero, MENSAJE_REQUISITOS)
        return

    # Si es un saludo o un mensaje muy genérico, no lo buscamos en
    # Mercado Libre: le pedimos que nos diga qué producto quiere.
    if es_saludo_o_generico(texto):
        enviar_texto(
            numero,
            "¡Hola! ¿Qué producto estás buscando? Contame la marca y el "
            "modelo (o lo que sepas) y te paso precio y cuotas.",
        )
        return

    # Si no, tratamos el mensaje como una búsqueda de producto nuevo.
    resultados = buscar_productos(texto, limite=3)

    if not resultados:
        enviar_texto(numero, "No encontré productos con esa descripción. ¿Podés darme más detalles?")
        return

    if len(resultados) == 1:
        producto = resultados[0]
        enviar_imagen(numero, producto["imagen"], caption=producto["titulo"])
        enviar_texto(numero, mensaje_precio(producto))
        return

    sesiones[numero] = resultados
    lista = "\n".join(f"{i + 1}. {p['titulo']}" for i, p in enumerate(resultados))
    enviar_texto(
        numero,
        f"Encontré estas opciones, decime el número de la que te sirve:\n\n{lista}",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
