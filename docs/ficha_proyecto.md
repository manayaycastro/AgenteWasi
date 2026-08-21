# Ficha breve del proyecto - AgenteWasi

**Fecha de aprobaciÃ³n:** 21 de agosto de 2026
**Repositorio:** https://github.com/manayaycastro/AgenteWasi

## Nombre

**AgenteWasi**

## Tipo de agente

Agente analista con herramientas desarrolladas en Python.

## Usuario objetivo

Propietario de un minimarket pequeÃ±o.

## Problema

El propietario registra sus ventas e inventario, pero revisar manualmente la informaciÃ³n le dificulta conocer sus ingresos, identificar los productos mÃ¡s vendidos, detectar existencias crÃ­ticas y decidir oportunamente quÃ© productos debe reponer.

## Propuesta de valor

Para el propietario de un minimarket, AgenteWasi analiza los registros de ventas e inventario mediante archivos CSV y herramientas de Python, entrega indicadores, alertas de stock y recomendaciones bÃ¡sicas de reposiciÃ³n, y evita presentar cifras no respaldadas por los datos disponibles.

## Entradas

- Preguntas del propietario en lenguaje natural.
- Periodo de anÃ¡lisis opcional.
- Archivo CSV ficticio de ventas.
- Archivo CSV ficticio de inventario.
- CÃ³digo y nombre ficticio del cliente, por ejemplo `CLI-001` y `Rosa Mendoza`.

## Salidas

- Total vendido por dÃ­a o periodo.
- Ranking de productos por unidades e ingresos.
- Ventas agrupadas por categorÃ­a.
- Alertas de productos agotados, crÃ­ticos, bajos o normales.
- Recomendaciones bÃ¡sicas y priorizadas de reposiciÃ³n.
- Productos con poca o ninguna venta.
- Clientes ficticios identificados por nombre con mayor frecuencia y gasto acumulado.
- Ticket promedio y porcentaje de clientes recurrentes.
- Mensajes claros ante datos invÃ¡lidos, ausentes o fuera de alcance.

## Herramientas previstas

- Carga y validaciÃ³n de archivos CSV.
- AnÃ¡lisis de ventas por producto, categorÃ­a, cliente y periodo.
- ClasificaciÃ³n del estado del inventario.
- CÃ¡lculo de stock objetivo y cantidad sugerida de reposiciÃ³n.
- CÃ¡lculo de indicadores de clientes con cÃ³digos y nombres ficticios.

## Reglas principales

### ClasificaciÃ³n del stock

- `AGOTADO`: `stock_actual = 0`.
- `CRITICO`: `stock_actual > 0` y `stock_actual <= stock_minimo`.
- `BAJO`: `stock_actual > stock_minimo` y `stock_actual <= stock_minimo * 1.5`.
- `NORMAL`: `stock_actual > stock_minimo * 1.5`.

### ReposiciÃ³n

- Solo se recomendarÃ¡ reponer productos agotados, crÃ­ticos o bajos.
- Se calcularÃ¡ la venta promedio diaria del periodo analizado.
- El stock objetivo serÃ¡ el mayor entre el doble del stock mÃ­nimo y siete dÃ­as de venta promedio.
- La cantidad sugerida serÃ¡ la diferencia positiva entre el stock objetivo y el stock actual, redondeada hacia arriba.
- Se priorizarÃ¡n productos agotados, despuÃ©s crÃ­ticos y finalmente bajos.
- AgenteWasi no realizarÃ¡ pedidos ni modificarÃ¡ el inventario.

## Fuera de alcance

- Predicciones mediante aprendizaje automÃ¡tico.
- AsesorÃ­a contable, tributaria, legal o financiera.
- Registro, modificaciÃ³n o eliminaciÃ³n automÃ¡tica de ventas e inventario.
- Pedidos automÃ¡ticos a proveedores.
- Uso de nombres reales, DNI, telÃ©fonos, correos, direcciones u otros datos personales.
- Respuestas basadas en informaciÃ³n que no exista en los archivos.
- Consultas ajenas a ventas, inventario, productos, categorÃ­as y clientes ficticios del minimarket.

## Riesgos

- Archivos incompletos o con columnas incorrectas.
- Valores negativos o tipos de datos invÃ¡lidos.
- Respuestas con cifras no respaldadas por las herramientas.
- ExposiciÃ³n accidental de credenciales.
- InterpretaciÃ³n de una recomendaciÃ³n como una decisiÃ³n automÃ¡tica.
- Conclusiones basadas en periodos con informaciÃ³n insuficiente.

## Controles

- ValidaciÃ³n de estructura, tipos y valores del CSV.
- Respuestas basadas en resultados calculados por herramientas.
- Reconocimiento explÃ­cito de datos ausentes.
- Variables de entorno para credenciales.
- Datos completamente ficticios; los nombres de clientes serÃ¡n inventados.
- Manejo de errores externos y consultas fuera de alcance.
- Recomendaciones informativas sujetas a decisiÃ³n humana.

## Siguientes pasos

1. DiseÃ±ar el diccionario de datos.
2. Construir y validar la data ficticia.
3. Preparar el entorno tÃ©cnico.
4. Implementar las herramientas Python.
5. Integrar el agente con Microsoft Foundry.
6. Ejecutar las pruebas funcionales y de error.
7. Completar la documentaciÃ³n del repositorio.
8. Grabar y entregar el video demostrativo.
