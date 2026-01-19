# Troubleshooting

Tabla documentada (síntoma → causa → acción):

| Síntoma | Causa probable | Acción |
|---|---|---|
| No inicia | `SERVI_URL_QA` no definido | Definir `SERVI_URL_QA` en `.env` |
| `skipped=true` | No cumple regla de aplicabilidad | Marcar `x_studio_servientrega` o carrier con nombre `SERVIENTREGA` |
| `502` sin guía | WS22 rechaza el cargue | Revisar mensajes de error del XML y validar datos de destinatario/remitente |
| No PDF | WS22 no retorna `bytesReport` | Revisar operación `GenerarGuiaSticker` y logs raw |
