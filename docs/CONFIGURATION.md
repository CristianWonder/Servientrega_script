# Configuración (Variables de entorno)

La configuración del servicio se maneja mediante variables de entorno.

## Odoo (JSON-RPC)
Variables documentadas:
- `ODOO_JSONRPC`: URL del endpoint JSON-RPC de Odoo (ej: `https://tuinstancia.odoo.com/jsonrpc`)
- `DB`: nombre de la base de datos
- `UID`: ID de usuario técnico (entero)
- `PWD`: password o token del usuario técnico
- `ODOO_TIMEOUT`: timeout HTTP hacia Odoo (segundos). Default 35

## Servientrega (WS22)
Variables documentadas:
- `SERVI_URL_QA`: URL WS22 de pruebas (**requerida por el webhook**)
- `SERVI_URL_PROD`: URL WS22 productiva (definida, pero no usada en el webhook actual)
- `SERVI_LOGIN`: usuario WS22
- `SERVI_PWD_ENC`: contraseña WS22
- `SERVI_COD_FACT`: Id_CodFacturacion
- `SERVI_TIMEOUT`: timeout HTTP hacia WS22 (segundos). Default 35/60

Nota: actualmente el webhook usa `SERVI_URL_QA` y no conmuta QA/PROD.

## Webhook
- `PORT`: puerto de escucha (default 5000)

## Archivo de ejemplo
Ver `.env.example` en la raíz del repositorio.
