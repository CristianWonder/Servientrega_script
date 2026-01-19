# Plan de pruebas

## Funcionales (caja negra)
Casos y resultados esperados:

1) **OK**
- Precondición: picking `done`, aplicable, sin tracking
- Esperado: `200 ok=true`, guía; tracking + PDF en Odoo

2) **No aplica**
- Precondición: no marcado y carrier no es Servientrega
- Esperado: `200 ok=true skipped=true`

3) **WS22 rechaza**
- Precondición: datos o credenciales inválidas
- Esperado: `502 ok=false`, detalle con mensajes extraídos

4) **Datos incompletos**
- Precondición: partner sin dirección o picking sin líneas
- Recomendado: `400` usando `validate_picking()` (hoy puede fallar más adelante)

## Técnicas (caja blanca)
Checks sugeridos:
- `safe_read/safe_write`: reintentos cuando existen campos Studio no presentes.
- `parsear_respuesta_ws22_xml()`: casos con `Num_Guia/NumeroGuia` y con errores `<string>`.
- Adjuntos: `create ir.attachment` con base64 y relación `res_model/res_id`.
