"""
Envío de mensajes usando la WhatsApp Cloud API de Meta.

Requiere dos variables de entorno:
- WHATSAPP_TOKEN: el token de acceso de tu app en Meta for Developers
- PHONE_NUMBER_ID: el ID del número de WhatsApp Business que vas a usar
"""

import os
import requests

WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
GRAPH_URL = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }


def enviar_texto(numero_destino: str, texto: str) -> dict:
    payload = {
        "messaging_product": "whatsapp",
        "to": numero_destino,
        "type": "text",
        "text": {"body": texto},
    }
    resp = requests.post(GRAPH_URL, headers=_headers(), json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()


def enviar_imagen(numero_destino: str, url_imagen: str, caption: str = "") -> dict:
    payload = {
        "messaging_product": "whatsapp",
        "to": numero_destino,
        "type": "image",
        "image": {"link": url_imagen, "caption": caption},
    }
    resp = requests.post(GRAPH_URL, headers=_headers(), json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()
