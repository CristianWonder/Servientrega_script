# Backlog técnico (mejoras recomendadas)

Lista documentada de mejoras:

1) Invocar `validate_picking()` antes de llamar WS22 (fallo temprano con mensajes claros).
2) Unificar SOAP reutilizando `servientrega_ws22.py` desde el webhook.
3) Conmutar QA/PROD (`SERVI_ENV`) y usar `SERVI_URL_PROD` en producción.
4) Parametrizar ciudad/departamento destino (no usar `11001000` fijo) y mapear códigos desde Odoo (idealmente DANE).
5) Implementar reintentos controlados y/o cola (Celery/Redis) para resiliencia.
