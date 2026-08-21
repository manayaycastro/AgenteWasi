# Reglas propuestas para generar la data - AgenteWasi

**Estado:** Aprobado y aplicado
**Periodo:** 01/01/2026 al 21/08/2026

## 1. Volumen propuesto

| Elemento | Cantidad o rango |
|---|---:|
| Productos | 35 |
| Clientes ficticios | 100 |
| Ventas por dÃ­a de lunes a jueves | 12 a 20 |
| Ventas por dÃ­a de viernes a domingo | 18 a 30 |
| Productos por venta | 1 a 5 |
| Operaciones estimadas en el periodo | 3,800 a 4,800 |
| Filas estimadas en `ventas_ejemplo.csv` | 8,000 a 11,000 |

Este volumen es suficiente para comparar meses, productos y clientes, pero continÃºa siendo manejable para Python y para la demostraciÃ³n.

## 2. Reglas de fechas y ventas

- Ninguna venta serÃ¡ anterior al 01/01/2026 ni posterior al 21/08/2026.
- `venta_id` serÃ¡ Ãºnico por operaciÃ³n y tendrÃ¡ el formato `VTA-000001`.
- Todas las filas de una venta compartirÃ¡n fecha, hora, cliente y mÃ©todo de pago.
- Una venta tendrÃ¡ entre uno y cinco productos diferentes.
- La cantidad por producto serÃ¡ un entero entre 1 y 6; el pan francÃ©s podrÃ¡ tener cantidades mayores, hasta 20.
- No se repetirÃ¡ el mismo `producto_id` dentro de una misma venta.
- El total de cada lÃ­nea serÃ¡ siempre positivo despuÃ©s del descuento.

## 3. Comportamiento temporal

- HabrÃ¡ ventas todos los dÃ­as del periodo para facilitar consultas por fecha.
- De viernes a domingo habrÃ¡ aproximadamente 30 % mÃ¡s operaciones que de lunes a jueves.
- Enero y febrero tendrÃ¡n mayor participaciÃ³n de bebidas.
- Marzo tendrÃ¡ mayor movimiento de productos de cuidado personal y snacks.
- Julio tendrÃ¡ un incremento moderado alrededor de Fiestas Patrias.
- Agosto solo incluirÃ¡ informaciÃ³n hasta el dÃ­a 21.
- La variaciÃ³n mensual serÃ¡ gradual, evitando saltos imposibles entre meses.

## 4. Clientes ficticios

- Se generarÃ¡n 100 clientes con cÃ³digos desde `CLI-001` hasta `CLI-100`.
- Cada cÃ³digo tendrÃ¡ un nombre ficticio Ãºnico y consistente.
- No se incluirÃ¡n DNI, telÃ©fono, correo, direcciÃ³n ni fecha de nacimiento.
- Aproximadamente 15 clientes serÃ¡n de alta frecuencia, 55 de frecuencia media y 30 ocasionales.
- Todos los clientes tendrÃ¡n al menos una venta.
- ExistirÃ¡n suficientes clientes con dos o mÃ¡s compras para calcular recurrencia.

## 5. Productos y rotaciÃ³n

- Las ventas solo utilizarÃ¡n los 35 productos aprobados.
- Productos cotidianos como pan, leche, arroz, agua y galletas tendrÃ¡n mayor probabilidad de venta.
- Productos de cuidado personal y limpieza tendrÃ¡n menor frecuencia, pero tickets unitarios mayores.
- Se reservarÃ¡n dos productos sin ventas en todo el periodo para probar la detecciÃ³n de productos sin movimiento.
- Se reservarÃ¡n tres productos con muy pocas ventas para probar baja rotaciÃ³n.
- Un producto agotado al 21/08/2026 puede tener ventas histÃ³ricas, porque se asume que hubo reposiciones durante el aÃ±o.
- El `stock_actual` es una fotografÃ­a al cierre y no se calcularÃ¡ restando todas las ventas histÃ³ricas.

## 6. Precios y descuentos

- El precio histÃ³rico se basarÃ¡ en el precio actual aprobado.
- Entre enero y abril algunos productos podrÃ¡n tener un precio entre 3 % y 8 % menor que el actual.
- Los precios se redondearÃ¡n a dos decimales y siempre serÃ¡n positivos.
- Aproximadamente 10 % de las lÃ­neas tendrÃ¡n descuento.
- El descuento serÃ¡ entre 2 % y 15 % del subtotal de la lÃ­nea.
- NingÃºn descuento podrÃ¡ igualar o superar el subtotal.

## 7. MÃ©todos de pago

DistribuciÃ³n aproximada:

| MÃ©todo | Porcentaje esperado |
|---|---:|
| EFECTIVO | 45 % |
| YAPE | 30 % |
| PLIN | 15 % |
| TARJETA | 10 % |

La distribuciÃ³n serÃ¡ aproximada, no una igualdad forzada.

## 8. Inventario al 21/08/2026

- Se conservarÃ¡n exactamente los `stock_actual` y `stock_minimo` aprobados en el catÃ¡logo.
- Todos los productos tendrÃ¡n `activo = TRUE`.
- La clasificaciÃ³n esperada serÃ¡ 6 agotados, 8 crÃ­ticos, 9 bajos y 12 normales.
- NingÃºn stock serÃ¡ negativo.

## 9. Reproducibilidad

- La generaciÃ³n utilizarÃ¡ una semilla aleatoria fija.
- Ejecutar nuevamente el generador con la misma semilla producirÃ¡ los mismos archivos.
- El script documentarÃ¡ la semilla y los parÃ¡metros utilizados.

## 10. Validaciones posteriores

- Fechas dentro del periodo.
- Columnas completas y tipos correctos.
- Identificadores de producto vÃ¡lidos.
- CÃ³digo y nombre de cliente consistentes.
- Importes y cantidades positivos.
- Coherencia entre las lÃ­neas de una misma venta.
- Totales de filas, ventas, clientes y productos documentados.
- Presencia de productos con alta, baja y ninguna rotaciÃ³n.
- Presencia de los cuatro estados de inventario.

## 11. Archivos generados

- `data/ventas_ejemplo.csv`
- `data/inventario_ejemplo.csv`
- `data/datos_invalidos_columnas.csv` para una prueba controlada de columna faltante.

## 12. AprobaciÃ³n y ejecuciÃ³n

Las reglas fueron aprobadas y aplicadas el 21 de agosto de 2026. La data se generÃ³ con la semilla fija `20260821`. Los resultados y validaciones estÃ¡n documentados en `docs/resumen_data.md`.
