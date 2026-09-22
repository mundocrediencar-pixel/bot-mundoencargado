# Bot de WhatsApp - Mundo Encargado

Bot que responde automáticamente a clientes por WhatsApp: busca el producto
en Mercado Libre, calcula el precio (costo + $40.000 de flete + 35%) y las
cuotas (6, 9 y 12), y responde con la foto y los montos.

## Archivos

- `app.py` — servidor Flask que recibe los mensajes (webhook de Meta)
- `mercadolibre.py` — búsqueda de productos en Mercado Libre
- `pricing.py` — la fórmula de precios y cuotas
- `whatsapp.py` — envío de mensajes por WhatsApp Cloud API

## 1. Variables de entorno necesarias

| Variable | Qué es | Dónde conseguirla |
|---|---|---|
| `WHATSAPP_TOKEN` | Token de acceso de tu app | Meta for Developers → tu app → WhatsApp → API Setup |
| `PHONE_NUMBER_ID` | ID del número de WhatsApp Business | Meta for Developers → tu app → WhatsApp → API Setup |
| `VERIFY_TOKEN` | Una palabra clave que vos inventás | La elegís vos (ej: `mundoencargado123`) |

## 2. Probarlo en tu computadora (opcional)

```bash
pip install -r requirements.txt
export WHATSAPP_TOKEN="tu_token"
export PHONE_NUMBER_ID="tu_phone_number_id"
export VERIFY_TOKEN="mundoencargado123"
python app.py
```

## 3. Subirlo a Render (gratis)

1. Subí esta carpeta a un repositorio de GitHub.
2. Entrá a [render.com](https://render.com) y creá una cuenta (podés usar GitHub para loguearte).
3. "New" → "Web Service" → elegís el repositorio.
4. Configurá:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. En "Environment", agregá las 3 variables de la tabla de arriba.
6. Deploy. Cuando termine, Render te da una URL tipo `https://tu-bot.onrender.com`.

## 4. Conectar el webhook en Meta

1. En Meta for Developers, tu app → WhatsApp → Configuration.
2. En "Webhook", poné:
   - **Callback URL:** `https://tu-bot.onrender.com/webhook`
   - **Verify Token:** el mismo valor que pusiste en `VERIFY_TOKEN`
3. Suscribite al campo `messages`.

Listo — a partir de ahí, cualquier mensaje que llegue a tu número de WhatsApp
Business va a activar el bot.

## Notas / próximos pasos

- El plan gratuito de Render "duerme" el servidor si no recibe tráfico por un
  rato; el primer mensaje después de una pausa puede tardar unos segundos más
  en responder.
- El estado de la conversación (qué opciones le mostramos a cada cliente) se
  guarda en memoria — si el servidor se reinicia, se pierde. Para más
  volumen, conviene pasarlo a una base de datos simple (ej: SQLite o Redis).
- El flete fijo de $40.000 está en `pricing.py` (`FLETE_FIJO`) — se puede
  cambiar ahí el día que varíe.
