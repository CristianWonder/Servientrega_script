# Arquitectura

## Resumen
Este servicio implementa la integración **Odoo → Servientrega WS22** para generar guías a partir de envíos (`stock.picking`) y persistir tracking + PDF + chatter en Odoo.

## Componentes
- **Odoo**: origen del evento (picking) y destino final de tracking/PDF.
- **Servicio Webhook (Flask)**: API HTTP que recibe el evento y coordina llamadas a Odoo y WS22.
- **Cliente Odoo JSON-RPC (`odoo_rpc.py`)**: wrapper de `execute_kw` con helpers `safe_*` para tolerar campos desconocidos (ej. Studio).
- **Servientrega WS22 (SOAP)**: servicio externo para crear guías y generar sticker PDF.

## Secuencia (end-to-end)
Diagrama de secuencia simplificado:

1. Odoo (automatización) → Webhook (Flask): `POST /webhook {id: picking_id}`
2. Webhook → Odoo JSON-RPC: `read stock.picking + res.partner + stock.move`
3. Webhook → WS22: `CargueMasivoExterno` (crear guía)
4. WS22 → Webhook: XML con guía o errores
5. Webhook → WS22: `GenerarGuiaSticker` (PDF base64)
6. Webhook → Odoo JSON-RPC: `write tracking + create ir.attachment + mail.message`

## Estructura del código (por archivo)
### `webhook_servientrega_ws22.py`
Responsabilidad: exponer endpoints HTTP y orquestar el flujo Odoo → WS22 → Odoo.

Funciones clave (resumen):
- `safe_read_one()`
- `validate_picking()` (implementada, pero **no se invoca** actualmente)
- `construir_payload_ws22()`
- `enviar_ws22_test()` (usa `SERVI_URL_QA`)
- `parsear_respuesta_ws22_xml()`
- `generar_pdf_guia()`
- `persistir_resultado_ws22()`

### `odoo_rpc.py`
Responsabilidad: encapsular JSON-RPC (`execute_kw`) con manejo de errores y tolerancia a campos desconocidos.

Operaciones expuestas: `read`, `search_read`, `write`, `create`, `safe_read`, `safe_write`, `message_post`, `write_tracking_ref`.

### `servientrega_ws22.py`
Responsabilidad: cliente WS22 reutilizable. Incluye:
- `create_shipment_envios_externo()`
- `generate_label_pdf()`

Nota: el webhook implementa SOAP en el mismo archivo y no importa este módulo; se recomienda unificar.
