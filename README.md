# WEBHOOK_SERVIENTREGA_WS22

Servicio **Flask** (API HTTP) que genera guías de **Servientrega WS22 (SOAP)** a partir de envíos (**`stock.picking`**) en **Odoo**.

Cuando Odoo crea o valida un envío, una automatización dispara un **webhook** hacia este servicio. El servicio consulta datos del envío en Odoo vía **JSON-RPC**, invoca WS22 para **crear la guía** (`CargueMasivoExterno`), solicita el **sticker en PDF** (`GenerarGuiaSticker`) y persiste el resultado de vuelta en Odoo (**tracking, URL, adjunto PDF y chatter**).

---

## Contenido

- [Características](#características)
- [Arquitectura](#arquitectura)
- [Endpoints](#endpoints)
- [Requisitos](#requisitos)
- [Ejecución local](#ejecución-local)
- [Configuración](#configuración)
- [Integración en Odoo](#integración-en-odoo)
- [Despliegue](#despliegue)
- [Operación y monitoreo](#operación-y-monitoreo)
- [Pruebas](#pruebas)
- [Troubleshooting](#troubleshooting)
- [Seguridad](#seguridad)
- [Documentación](#documentación)

---

## Características

- Recepción de eventos desde Odoo vía webhook (`POST /webhook`).
- Lectura en Odoo vía JSON-RPC: `stock.picking`, `res.partner`, `stock.move`.
- Creación de guía WS22: `CargueMasivoExterno`.
- Generación de sticker PDF WS22: `GenerarGuiaSticker`.
- Persistencia en Odoo:
  - `carrier_tracking_ref` (guía) y `carrier_tracking_url` (rastreo)
  - campos Studio (si existen)
  - adjunto PDF en `ir.attachment`
  - mensaje en chatter (`mail.message`)

Fuera de alcance (diseño actual):
- Ejecución asíncrona (no hay cola/reintentos; ejecución síncrona en el request).
- Parametrización completa de códigos de ciudad/departamento (hay valores fijos en el SOAP).
- Autenticación/autorización del webhook (no se valida token/firma).

---

## Arquitectura

Secuencia simplificada:
1. **Odoo (Automatización)** → **Webhook (Flask)**: `POST /webhook {id: picking_id}`
2. **Webhook** → **Odoo JSON-RPC**: `read` de `stock.picking` + `res.partner` + `stock.move`
3. **Webhook** → **Servientrega WS22**: `CargueMasivoExterno` (crear guía)
4. **Servientrega** → **Webhook**: XML con número de guía o errores
5. **Webhook** → **Servientrega WS22**: `GenerarGuiaSticker` (PDF base64)
6. **Webhook** → **Odoo JSON-RPC**: `write` tracking + `create` `ir.attachment` + `mail.message`

Ver detalle: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

---

## Endpoints

Endpoints expuestos por el servicio:

- `GET /health` → estado del servicio
- `GET /ping` → `PONG`
- `POST /webhook` → procesa un `picking_id`

Payload mínimo esperado:
```json
{"id": 241}
```

Códigos de respuesta (actuales):
- `200` OK con guía → `{"ok": true, "guia": "...", "url": "..."}`
- `200` No aplica → `{"ok": true, "skipped": true}`
- `400` Payload inválido / faltan datos críticos → `{"error": "...", "detail": "..."}`
- `502` WS22 falla / no retorna guía → `{"ok": false, "detail": {...}}`

Ver detalle: [`docs/API.md`](docs/API.md)

---

## Requisitos

- Linux (Ubuntu recomendado)
- Python **3.10+**
- Conectividad HTTPS a Odoo y WS22

Dependencias mínimas recomendadas:
- `flask`
- `requests`
- `python-dotenv`

---

## Ejecución local

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Variables de entorno en .env
python webhook_servientrega_ws22.py
```

Verificación rápida:
```bash
curl -s http://localhost:5000/health
curl -s http://localhost:5000/ping
curl -s -X POST http://localhost:5000/webhook \
  -H 'Content-Type: application/json' \
  -d '{"id":241}'
```

---

## Configuración

El servicio usa **variables de entorno** (ver `.env.example`). Variables documentadas en el documento técnico:

### Odoo (JSON-RPC)
- `ODOO_JSONRPC` (ej: `https://tuinstancia.odoo.com/jsonrpc`)
- `DB`
- `UID`
- `PWD`
- `ODOO_TIMEOUT` (default 35)

### Servientrega (WS22)
- `SERVI_URL_QA` (**requerida por el webhook**)
- `SERVI_URL_PROD` (definida, pero no usada en el webhook actual)
- `SERVI_LOGIN`
- `SERVI_PWD_ENC`
- `SERVI_COD_FACT`
- `SERVI_TIMEOUT` (default 35/60)

### Webhook
- `PORT` (default 5000)

Nota: actualmente el webhook usa `SERVI_URL_QA` y no conmuta QA/PROD.

Ver detalle: [`docs/CONFIGURATION.md`](docs/CONFIGURATION.md)

---

## Integración en Odoo

Se requiere una automatización en Odoo para invocar el webhook al validar/crear el envío.

Recomendación (trigger y dominio):
- Modelo: `stock.picking`
- Trigger sugerido: `On Update` (al pasar a `state=done`)
- Dominio sugerido: `[("state","=","done"), ("carrier_tracking_ref","=",False)]`

Ejemplo (Server Action - Python):
```python
import requests
WEBHOOK_URL = "https://<tu-dominio>/webhook"
requests.post(WEBHOOK_URL, json={"id": record.id}, timeout=20)
```

Ver detalle: [`docs/ODOO_SETUP.md`](docs/ODOO_SETUP.md)

---

## Despliegue

En producción se recomienda ejecutar con un servidor WSGI (por ejemplo, **Gunicorn**) y exponer con **nginx**, evitando `debug=True`.

Ver guía: [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md)

---

## Operación y monitoreo

Recomendaciones de operación:
- Logs en stdout (INFO). Centralización y rotación.
- Procesamiento síncrono: considerar timeouts y límites del proxy.
- Verificar conectividad del servidor a WS22 y Odoo.

---

## Pruebas

Plan de pruebas resumido (funcionales y técnicas):

Ver detalle: [`docs/TESTING.md`](docs/TESTING.md)

---

## Troubleshooting

Guía rápida y síntomas comunes:

Ver detalle: [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md)

---

## Seguridad

Recomendaciones (documentadas):
- Autenticación del webhook (token estático, firma HMAC o allowlist por IP)
- Evitar loggear credenciales WS22 en producción
- Exponer solo por HTTPS detrás de un reverse proxy

Ver detalle: [`docs/SECURITY.md`](docs/SECURITY.md)

---

## Documentación

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/API.md`](docs/API.md)
- [`docs/CONFIGURATION.md`](docs/CONFIGURATION.md)
- [`docs/ODOO_SETUP.md`](docs/ODOO_SETUP.md)
- [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md)
- [`docs/OPERATIONS.md`](docs/OPERATIONS.md)
- [`docs/TESTING.md`](docs/TESTING.md)
- [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md)
- [`docs/SECURITY.md`](docs/SECURITY.md)
- [`docs/BACKLOG.md`](docs/BACKLOG.md)

---

## Changelog

Ver [`CHANGELOG.md`](CHANGELOG.md). Formato basado en *Keep a Changelog* y versionado SemVer (referencias externas en la conversación).
