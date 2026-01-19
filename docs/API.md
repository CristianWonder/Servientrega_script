# API (Webhook)

## Endpoints
Endpoints expuestos por el servicio Flask:

### `GET /health`
- Propósito: health check del servicio
- Resultado esperado: status ok

### `GET /ping`
- Propósito: verificación rápida
- Respuesta: `PONG`

### `POST /webhook`
- Propósito: procesa un `picking_id`
- Payload mínimo esperado:
  ```json
  {"id": 241}
  ```

## Respuestas HTTP (actuales)
Tabla resumida:

- **200** Proceso OK con guía
  ```json
  {"ok": true, "guia": "...", "url": "..."}
  ```
- **200** No aplica a Servientrega
  ```json
  {"ok": true, "skipped": true}
  ```
- **400** Payload inválido / faltan datos críticos
  ```json
  {"error": "...", "detail": "..."}
  ```
- **502** WS22 no retorna guía / falla externa
  ```json
  {"ok": false, "detail": {"...": "..."}}
  ```

## Regla de aplicabilidad
El webhook procesa el picking solo si se cumple al menos una condición:
- `x_studio_servientrega == True` (si el campo existe)
- `carrier_id.name` contiene `SERVIENTREGA`

Si no cumple, responde `ok=true, skipped=true`.
