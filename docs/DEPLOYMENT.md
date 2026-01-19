# Despliegue

## Recomendación base
Para producción se recomienda ejecutar el servicio con un servidor WSGI (por ejemplo, Gunicorn) y exponerlo detrás de un reverse proxy (por ejemplo, nginx), evitando `debug=True`.

## Enfoque sugerido
1) Servicio (Gunicorn) escuchando en localhost (ej. `127.0.0.1:5000` o `127.0.0.1:8000`).
2) Reverse proxy (nginx) exponiendo HTTPS público y reenviando a Gunicorn.

## Checklist
- Variables de entorno configuradas (ver `docs/CONFIGURATION.md`).
- Timeouts del proxy alineados con la latencia esperada de Odoo + WS22 (el flujo es síncrono).
- Logs centralizados/rotados.

## Ejemplos
El documento técnico no incluye ejemplos completos de Gunicorn/nginx. Esta guía deja el despliegue como estándar WSGI + reverse proxy.
