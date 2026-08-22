# Seguridad, límites y costos

## Protección de credenciales

- Las credenciales se almacenan únicamente en el archivo local `.env`.
- `.env` y `.venv` están excluidos mediante `.gitignore`.
- `.env.example` contiene solamente nombres de variables y valores de ejemplo.
- No se encontraron claves ni endpoints reales en los archivos versionados.
- Las claves no deben compartirse en capturas, videos, documentación o mensajes.

## Privacidad de los datos

- Todos los datos del minimarket son ficticios.
- Los clientes tienen códigos y nombres inventados.
- No se utilizan DNI, teléfonos, correos, direcciones ni información personal real.

## Límites funcionales

- AgenteWasi analiza solamente los archivos CSV configurados.
- No predice ventas mediante aprendizaje automático.
- No brinda asesoría contable, tributaria, legal ni financiera.
- No modifica ventas o inventario.
- No genera pedidos automáticos.
- Las recomendaciones de reposición son informativas y deben ser revisadas por el propietario.
- Si faltan datos, el agente debe indicarlo en lugar de inventar resultados.

## Límite recomendado para archivos

Para la demostración se recomienda utilizar archivos CSV de hasta 10 MB por archivo. Los archivos más grandes pueden aumentar el tiempo de carga y el consumo de memoria.

## Manejo de servicios externos

Si Azure OpenAI no está disponible, la aplicación muestra un mensaje controlado y permite continuar o finalizar la conversación. Los cálculos Python pueden probarse independientemente del modelo.

## Costos

El deployment utiliza modalidad Estándar global con pago por consumo. Los 5000 TPM representan un límite de velocidad, no un presupuesto monetario.

El proyecto utiliza el crédito promocional de Azure de USD 200. Se debe revisar periódicamente Cost Management, evitar capacidad aprovisionada y detener otros recursos de Azure que no estén en uso.

El costo exacto depende de los tokens de entrada y salida y debe verificarse en la página de precios de Azure antes de utilizar el proyecto fuera de la demostración.
