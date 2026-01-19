# Seguridad

## Estado actual
El diseño actual no valida token/firma (no hay autenticación/autorización del webhook).

## Recomendaciones documentadas
- Agregar autenticación al webhook:
  - token estático
  - firma HMAC
  - allowlist por IP
- Evitar loggear credenciales WS22 en producción (enmascarar o bajar el nivel de log).
- Exponer el servicio solo por HTTPS detrás de un reverse proxy.

## Buenas prácticas mínimas para el repo
- No incluir secretos en commits.
- Mantener `.env` fuera del control de versiones.
- Mantener `.env.example` actualizado.
