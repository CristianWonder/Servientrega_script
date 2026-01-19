# Operación, monitoreo y soporte

Recomendaciones documentadas:

- **Logs**: stdout (INFO). Recomendada centralización y rotación.
- **Procesamiento síncrono**: considerar timeouts y límites del proxy.
- **Conectividad**: revisar acceso a internet hacia WS22 y hacia Odoo.

## Señales a monitorear
- Tasa de respuestas `502` (WS22 no retorna guía / falla externa).
- Tasa de `skipped=true` (picking no aplicable por regla de aplicabilidad).
- Latencia del endpoint `POST /webhook` (impacta el trigger en Odoo).

## Idempotencia
Se recomienda evitar ejecución repetida verificando `carrier_tracking_ref` y/o usando una marca adicional (campo boolean) si es necesario.
