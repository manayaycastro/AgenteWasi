# Diccionario de datos - AgenteWasi

**Estado:** Aprobado
**Fecha:** 21 de agosto de 2026

## 1. Objetivo

Definir la estructura, tipos y reglas de calidad de los datos ficticios que utilizarÃ¡ AgenteWasi para analizar ventas, inventario e indicadores de clientes ficticios de un minimarket.

Se proponen dos archivos CSV relacionados mediante el campo `producto_id`:

1. `ventas_ejemplo.csv`: una fila por producto incluido en una venta.
2. `inventario_ejemplo.csv`: una fila por producto del minimarket.

## 2. Archivo `ventas_ejemplo.csv`

### Granularidad

Cada fila representa un producto vendido dentro de una operaciÃ³n de venta. Una misma venta puede aparecer en varias filas cuando incluye mÃ¡s de un producto; esas filas compartirÃ¡n el mismo `venta_id`.

| Campo | Tipo | Obligatorio | Ejemplo | DescripciÃ³n y regla |
|---|---|---:|---|---|
| `venta_id` | Texto | SÃ­ | `VTA-0001` | Identificador de la operaciÃ³n. Puede repetirse en los productos de la misma venta. |
| `fecha` | Fecha | SÃ­ | `2026-07-01` | Formato ISO `AAAA-MM-DD`. No puede estar fuera del periodo definido. |
| `hora` | Hora | SÃ­ | `09:35:00` | Formato `HH:MM:SS`, entre `00:00:00` y `23:59:59`. |
| `cliente_id` | Texto | SÃ­ | `CLI-001` | CÃ³digo ficticio y anÃ³nimo. No contiene informaciÃ³n personal. |
| `cliente_nombre` | Texto | SÃ­ | `Rosa Mendoza` | Nombre completamente ficticio que se mostrarÃ¡ en los indicadores. Debe mantenerse igual para un mismo `cliente_id`. |
| `producto_id` | Texto | SÃ­ | `PROD-001` | Debe existir en `inventario_ejemplo.csv`. |
| `cantidad` | Entero | SÃ­ | `2` | Unidades vendidas. Debe ser mayor que cero. |
| `precio_unitario` | Decimal | SÃ­ | `4.50` | Precio de venta por unidad en soles. Debe ser mayor que cero y tener mÃ¡ximo dos decimales. |
| `descuento` | Decimal | SÃ­ | `0.00` | Descuento monetario aplicado a la fila. Debe ser mayor o igual a cero y menor que `cantidad * precio_unitario`. |
| `metodo_pago` | CategorÃ­a | SÃ­ | `YAPE` | Valores permitidos: `EFECTIVO`, `YAPE`, `PLIN` o `TARJETA`. |

### Campos calculados, no almacenados

| Indicador | FÃ³rmula |
|---|---|
| `subtotal_bruto` | `cantidad * precio_unitario` |
| `total_linea` | `(cantidad * precio_unitario) - descuento` |
| `total_venta` | Suma de `total_linea` agrupada por `venta_id` |
| `ticket_promedio` | Promedio de `total_venta` por operaciÃ³n |

### Ejemplo conceptual

```csv
venta_id,fecha,hora,cliente_id,cliente_nombre,producto_id,cantidad,precio_unitario,descuento,metodo_pago
VTA-0001,2026-07-01,09:35:00,CLI-001,Rosa Mendoza,PROD-001,2,4.50,0.00,YAPE
VTA-0001,2026-07-01,09:35:00,CLI-001,Rosa Mendoza,PROD-005,1,8.90,0.50,YAPE
```

## 3. Archivo `inventario_ejemplo.csv`

### Granularidad

Cada fila representa un producto Ãºnico disponible o registrado en el catÃ¡logo del minimarket.

| Campo | Tipo | Obligatorio | Ejemplo | DescripciÃ³n y regla |
|---|---|---:|---|---|
| `producto_id` | Texto | SÃ­ | `PROD-001` | Identificador Ãºnico del producto. No puede repetirse. |
| `producto` | Texto | SÃ­ | `Leche evaporada 400 g` | Nombre ficticio y legible del producto. |
| `categoria` | CategorÃ­a | SÃ­ | `LACTEOS` | CategorÃ­a comercial definida para el proyecto. |
| `unidad_medida` | CategorÃ­a | SÃ­ | `UNIDAD` | Valores propuestos: `UNIDAD`, `PAQUETE`, `BOTELLA`, `BOLSA`, `LATA` o `CAJA`. |
| `precio_venta_actual` | Decimal | SÃ­ | `4.50` | Precio vigente de referencia en soles. Mayor que cero. |
| `stock_actual` | Entero | SÃ­ | `8` | Existencias actuales. Debe ser mayor o igual a cero. |
| `stock_minimo` | Entero | SÃ­ | `10` | Umbral definido para el producto. Debe ser mayor que cero. |
| `activo` | Booleano | SÃ­ | `TRUE` | Valores permitidos: `TRUE` o `FALSE`. |

### Estado calculado del stock

| Estado | Regla |
|---|---|
| `AGOTADO` | `stock_actual = 0` |
| `CRITICO` | `stock_actual > 0` y `stock_actual <= stock_minimo` |
| `BAJO` | `stock_actual > stock_minimo` y `stock_actual <= stock_minimo * 1.5` |
| `NORMAL` | `stock_actual > stock_minimo * 1.5` |

### Ejemplo conceptual

```csv
producto_id,producto,categoria,unidad_medida,precio_venta_actual,stock_actual,stock_minimo,activo
PROD-001,Leche evaporada 400 g,LACTEOS,LATA,4.50,8,10,TRUE
```

## 4. RelaciÃ³n entre archivos

- `inventario_ejemplo.csv.producto_id` es la referencia maestra de productos.
- Todo `producto_id` utilizado en ventas debe existir en inventario.
- Un producto puede existir en inventario sin registrar ventas; esto permitirÃ¡ detectar productos con poca o ninguna venta.
- El precio histÃ³rico del anÃ¡lisis se tomarÃ¡ de `ventas_ejemplo.csv.precio_unitario`, no del precio actual del inventario.

## 5. Reglas para indicadores de clientes

- Un cliente se identifica tÃ©cnicamente mediante `cliente_id` y se muestra mediante `cliente_nombre`.
- Todos los nombres serÃ¡n inventados para el proyecto y no representarÃ¡n personas reales.
- No se almacenarÃ¡n DNI, telÃ©fonos, correos, direcciones ni fechas de nacimiento.
- Cada `cliente_id` deberÃ¡ relacionarse siempre con un Ãºnico `cliente_nombre`.
- Un cliente recurrente serÃ¡ aquel que aparezca en dos o mÃ¡s `venta_id` diferentes durante el periodo analizado.
- Frecuencia de compra: cantidad de `venta_id` distintos por cliente.
- Gasto acumulado: suma de los totales de las ventas asociadas al cliente.
- Ticket promedio por cliente: gasto acumulado dividido entre su cantidad de ventas.
- Porcentaje de clientes recurrentes: clientes con dos o mÃ¡s ventas dividido entre el total de clientes, multiplicado por 100.

## 6. Reglas generales de calidad

- CodificaciÃ³n UTF-8.
- Separador: coma.
- Encabezados en minÃºsculas y formato `snake_case`.
- Fechas en formato ISO `AAAA-MM-DD`.
- Decimales con punto y mÃ¡ximo dos posiciones.
- No se permiten valores negativos.
- No se permiten campos obligatorios vacÃ­os.
- No se permiten identificadores de producto huÃ©rfanos.
- Todas las filas de una misma `venta_id` deben compartir fecha, hora, cÃ³digo y nombre del cliente, y mÃ©todo de pago.
- Los datos serÃ¡n completamente ficticios y publicables.

## 7. CategorÃ­as iniciales propuestas

- `ABARROTES`
- `BEBIDAS`
- `LACTEOS`
- `LIMPIEZA`
- `CUIDADO_PERSONAL`
- `SNACKS`
- `PANADERIA`

## 8. Decisiones pendientes posteriores

Estas decisiones se tomarÃ¡n despuÃ©s de aprobar el diccionario:

- Cantidad de productos, clientes, ventas y filas.
- Productos especÃ­ficos de cada categorÃ­a.
- DistribuciÃ³n de mÃ©todos de pago.
- Casos intencionales de productos agotados, crÃ­ticos, bajos y normales.
- Archivo invÃ¡lido para las pruebas de error.

### Periodo aprobado

- Fecha inicial: `2026-01-01`.
- Fecha final: `2026-08-21`.
- Incluye todos los meses transcurridos de 2026 hasta la fecha de corte.

## 9. AprobaciÃ³n

El diccionario fue aprobado el 21 de agosto de 2026. Todas las columnas definidas en esta versiÃ³n son obligatorias. Cualquier cambio posterior deberÃ¡ registrarse antes de generar o regenerar los archivos CSV.
