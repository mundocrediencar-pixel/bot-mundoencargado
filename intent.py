"""
Detección simple de intención: distingue un saludo, una pregunta por
crédito en efectivo, una pregunta por los requisitos del crédito
personal para comprar un producto, o una búsqueda real de producto.
Esto evita mandarle saludos o preguntas administrativas a la API de
Mercado Libre.
"""

import re

# Palabras "de relleno": saludos, conectores y verbos de búsqueda que
# por sí solos no dicen qué producto quiere el cliente.
PALABRAS_RELLENO = {
    "hola", "buenas", "buen", "buenos", "buenas", "dia", "día", "dias",
    "días", "tardes", "noches", "hey", "que", "qué", "tal", "como",
    "cómo", "estas", "estás", "andas", "andás", "todo", "bien",
    "busco", "buscando", "necesito", "quiero", "quisiera", "estoy",
    "tenes", "tenés", "tienen", "hay", "vendes", "vendés", "venden",
    "precio", "consulta", "consultar", "consultarte", "producto",
    "un", "una", "unos", "unas", "algo", "porfa", "porfavor", "favor",
    "por", "gracias", "che", "disculpa", "disculpe",
}

# Palabras que indican que preguntan puntualmente por crédito EN
# EFECTIVO (dinero), no por comprar un producto a crédito.
PALABRAS_EFECTIVO = {"efectivo", "cash", "plata", "dinero"}

# Palabras clave que indican que preguntan por los requisitos del
# crédito personal (documentación necesaria), no por un producto.
PISTAS_REQUISITOS = {
    "requisito", "requisitos", "papeles", "documentacion", "documentación",
}


def _normalizar(texto: str) -> str:
    texto = texto.lower().strip()
    texto = re.sub(r"[^\wáéíóúñ ]", "", texto)
    return texto


def es_consulta_credito_efectivo(texto: str) -> bool:
    """
    True si el cliente pregunta por crédito EN EFECTIVO (plata,
    dinero), que no tiene que ver con la compra de un producto.
    Ej: "hacen credito en efectivo?", "necesito plata prestada",
    "dan credito en efectivo tambien?".
    """
    normalizado = _normalizar(texto)
    if not normalizado:
        return False

    palabras = set(normalizado.split())

    menciona_credito = "credito" in palabras or "crédito" in palabras
    menciona_efectivo = bool(palabras & PALABRAS_EFECTIVO)

    return menciona_credito and menciona_efectivo


def es_consulta_requisitos(texto: str) -> bool:
    """
    True si el cliente está preguntando por los requisitos o la
    documentación necesaria para acceder al crédito personal para
    comprar un producto.
    Ej: "que necesito para el credito", "cuales son los requisitos",
    "que documentacion piden", "que papeles hay que llevar".
    """
    normalizado = _normalizar(texto)
    if not normalizado:
        return False

    palabras = set(normalizado.split())

    # Si en realidad está preguntando por crédito en efectivo, no es
    # una consulta de requisitos para comprar un producto.
    if es_consulta_credito_efectivo(texto):
        return False

    # Menciona directamente "requisitos", "papeles" o "documentación".
    if palabras & PISTAS_REQUISITOS:
        return True

    # Menciona "crédito" junto con una pregunta de qué se necesita.
    menciona_credito = "credito" in palabras or "crédito" in palabras
    pregunta_que_necesita = any(
        p in palabras for p in ("necesito", "necesita", "piden", "pide", "llevar")
    )
    if menciona_credito and pregunta_que_necesita:
        return True

    return False


def es_saludo_o_generico(texto: str) -> bool:
    """
    True si el mensaje es un saludo o algo demasiado genérico como
    para buscarlo en Mercado Libre (ej: "hola", "buen día",
    "hola buen día estoy buscando un producto").

    La idea: sacamos todas las palabras de relleno (saludos, "busco",
    "un", "producto", etc). Si no queda ninguna palabra específica
    (una marca, un tipo de producto, un modelo), es genérico.
    """
    normalizado = _normalizar(texto)

    if not normalizado:
        return True

    palabras = normalizado.split()
    palabras_especificas = [p for p in palabras if p not in PALABRAS_RELLENO]

    return len(palabras_especificas) == 0
