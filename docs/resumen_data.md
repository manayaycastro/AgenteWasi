# Resumen y validaciÃ³n de la data - AgenteWasi

**Fecha de generaciÃ³n:** 21 de agosto de 2026
**Semilla:** `20260821`
**Periodo:** 01/01/2026 al 21/08/2026
**Naturaleza:** datos completamente ficticios

## Archivos generados

| Archivo | Registros sin encabezado | SHA-256 |
|---|---:|---|
| `data/ventas_ejemplo.csv` | 10,475 lÃ­neas de productos | `63c307745e55c582f03809a9a3c5e2d6e65d8d412634cd623cc272b3e0f0f9d9` |
| `data/inventario_ejemplo.csv` | 35 productos | `8db397ad13145d6d8b5ac66ccff858911c175b0b0240c4dbe56d17435fbb3c91` |
| `data/datos_invalidos_columnas.csv` | 4 registros de prueba | `7c257b2842bde73ab8e4117fb3ac1b3ccc3ddebe7738c458253f81edd7e3f019` |

## Resultados generales

| Indicador | Resultado |
|---|---:|
| Operaciones de venta | 4,571 |
| LÃ­neas de productos vendidas | 10,475 |
| Clientes ficticios | 100 |
| Productos del catÃ¡logo | 35 |
| Ventas netas generadas | S/ 160,744.45 |
| Productos sin ventas | 2 |

## Operaciones por mes

| Mes | Ventas |
|---|---:|
| Enero 2026 | 574 |
| Febrero 2026 | 578 |
| Marzo 2026 | 592 |
| Abril 2026 | 587 |
| Mayo 2026 | 622 |
| Junio 2026 | 608 |
| Julio 2026 | 609 |
| Agosto 2026, hasta el dÃ­a 21 | 401 |
| Total | 4,571 |

## MÃ©todos de pago

| MÃ©todo | Operaciones | ParticipaciÃ³n aproximada |
|---|---:|---:|
| EFECTIVO | 2,047 | 44.8 % |
| YAPE | 1,382 | 30.2 % |
| PLIN | 688 | 15.1 % |
| TARJETA | 454 | 9.9 % |
| Total | 4,571 | 100.0 % |

## Estados del inventario

| Estado | Productos |
|---|---:|
| AGOTADO | 6 |
| CRITICO | 8 |
| BAJO | 9 |
| NORMAL | 12 |
| Total | 35 |

## Casos intencionales para la demostraciÃ³n

- `PROD-025` y `PROD-035` no registran ventas en todo el periodo.
- `PROD-021`, `PROD-024` y `PROD-030` tienen probabilidades muy bajas de venta.
- Existen productos agotados, crÃ­ticos, bajos y normales.
- Hay clientes de frecuencia alta, media y ocasional.
- Las ventas cubren todos los dÃ­as desde el 01/01/2026 hasta el 21/08/2026.

## Validaciones aprobadas

- Fecha inicial y final exactas.
- Ocho meses representados.
- 100 cÃ³digos de clientes asociados consistentemente con 100 nombres ficticios.
- 35 productos vÃ¡lidos y relacionados con el inventario.
- Dos productos sin movimiento.
- Cantidades, precios y descuentos vÃ¡lidos.
- Cabeceras consistentes en todas las lÃ­neas de una misma venta.
- DistribuciÃ³n esperada de estados de stock.
- RevisiÃ³n visual legible de ambos archivos.
- Ausencia de DNI, telÃ©fono, correo, direcciÃ³n y otros datos personales reales.

## Limitaciones

- El inventario es una fotografÃ­a al 21/08/2026 y no un kardex histÃ³rico.
- Se asume que existieron reposiciones durante el aÃ±o.
- Los precios, clientes, productos y patrones son ficticios.
- La data sirve para demostraciÃ³n y pruebas; no representa resultados de un negocio real.

## Archivo invÃ¡lido controlado

`data/datos_invalidos_columnas.csv` reproduce un Ãºnico error estructural: omite la columna obligatoria `cantidad`. Conserva las otras nueve columnas de ventas y contiene cuatro registros coherentes. Su resultado esperado es que AgenteWasi rechace el archivo e indique claramente que falta `cantidad`.
