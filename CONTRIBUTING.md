# Contribuir

## Alcance
Este repositorio contiene un servicio Flask que integra Odoo (JSON-RPC) con Servientrega WS22 (SOAP) para generar guías y sticker PDF.

## Flujo de cambios
1. Crear rama por cambio (feature/fix).
2. Mantener cambios pequeños y revisables.
3. Actualizar documentación si se modifica:
   - API (`docs/API.md`)
   - Variables de entorno (`docs/CONFIGURATION.md`)
   - Flujo/arquitectura (`docs/ARCHITECTURE.md`)
   - Operación (`docs/OPERATIONS.md`)
4. Actualizar `CHANGELOG.md` en `[Unreleased]`.

## Criterios mínimos
- No incluir secretos en commits.
- Mantener la ejecución local funcionando (`python webhook_servientrega_ws22.py`).
- Verificar endpoints:
  - `GET /health`
  - `GET /ping`
  - `POST /webhook` con un `id` válido.
