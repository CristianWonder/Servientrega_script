# Configuración en Odoo (Automatización / Server Action)

## Objetivo
Ejecutar una automatización en Odoo al validar/crear el envío para invocar el webhook.

## Recomendación de trigger y dominio
- **Modelo**: `stock.picking`
- **Trigger sugerido**: `On Update` (al pasar a `state=done`)
- **Dominio sugerido**: `[("state","=","done"), ("carrier_tracking_ref","=",False)]`

## Ejemplo (Server Action - Python)
Ejemplo referencial. Ajustar URL, timeout y condiciones según política interna.

```python
import requests
WEBHOOK_URL = "https://<tu-dominio>/webhook"
requests.post(WEBHOOK_URL, json={"id": record.id}, timeout=20)

# Recomendación: evitar ejecución repetida verificando carrier_tracking_ref
# y/o usando una marca adicional (campo boolean) si es necesario.
```
