# Matriz de pruebas de AgenteWasi

**Fecha:** 21 de agosto de 2026  
**Entorno:** Windows, Python 3.12.10  
**Modelo:** gpt-4.1-mini  
**Deployment:** agentewasi-gpt41-mini  
**Resultado automatizado:** 102 pruebas aprobadas  

## Objetivo

Comprobar que AgenteWasi carga y valida los archivos CSV, calcula resultados verificables, utiliza las herramientas Python, controla entradas inválidas y responde mediante Microsoft Foundry sin modificar los datos originales.

## Matriz de pruebas

| ID | Caso | Entrada o acción | Resultado esperado | Resultado obtenido | Estado |
|---|---|---|---|---|---|
| P-01 | Carga de ventas | Cargar `ventas_ejemplo.csv` | 10475 filas y 10 columnas | 10475 filas y 10 columnas | Aprobado |
| P-02 | Carga de inventario | Cargar `inventario_ejemplo.csv` | 35 productos y 8 columnas | 35 productos y 8 columnas | Aprobado |
| P-03 | Columnas faltantes | Cargar `datos_invalidos_columnas.csv` | Rechazar e informar que falta `cantidad` | Se informó la columna `cantidad` | Aprobado |
| P-04 | Ventas por fecha | Consultar ventas del 21/08/2026 | Calcular el total usando el CSV | S/ 802.16 y 20 ventas | Aprobado |
| P-05 | Productos más vendidos | Solicitar los cinco primeros | Mostrar ranking por unidades e ingresos | Ranking generado con nombres y códigos | Aprobado |
| P-06 | Stock crítico | Consultar productos críticos | Clasificar agotados, críticos y bajos | Clasificación y faltantes calculados | Aprobado |
| P-07 | Reposición | Consultar qué productos reponer | Calcular cantidades sugeridas sin crear pedidos | Recomendaciones informativas generadas | Aprobado |
| P-08 | Indicadores de clientes | Consultar compras, gasto y recurrencia | Calcular indicadores usando clientes ficticios | Indicadores y rankings generados | Aprobado |
| P-09 | Servicio no disponible | Interrumpir temporalmente la conexión con Azure | Mostrar un error comprensible sin cerrar la CLI | Se controló `APITimeoutError` | Aprobado |
| P-10 | Ejecución conversacional | Ejecutar `python -m agentewasi` y realizar una consulta | El agente debe seleccionar una herramienta y responder | Respuesta obtenida mediante Azure OpenAI | Aprobado |
| P-11 | Salida controlada | Escribir `salir` | Finalizar la conversación correctamente | Se mostró `Conversación finalizada` | Aprobado |
| P-12 | Suite automatizada | Ejecutar `python -m pytest -q` | Todas las pruebas deben aprobar | 102 pruebas aprobadas | Aprobado |

## Evidencia automatizada

Comando ejecutado:

```powershell
python -m pytest -q
```

## Evidencia de instalación

El proyecto fue instalado en modo editable:

```powershell
python -m pip install -e . --no-build-isolation
```

Resultado:

```text
Successfully installed agentewasi-0.1.0
```

## Evidencia conversacional

Pregunta:

```text
¿Cuánto se vendió el 21 de agosto de 2026?
```

La respuesta fue calculada desde los archivos CSV mediante una herramienta Python y redactada por el modelo desplegado en Microsoft Foundry.

## Conclusión

Los casos principales y de error fueron aprobados. AgenteWasi ejecuta cálculos deterministas, controla archivos inválidos, maneja fallos externos y proporciona una interfaz CLI reproducible.
