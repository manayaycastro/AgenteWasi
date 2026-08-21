# CatÃ¡logo propuesto de productos - AgenteWasi

**Estado:** Aprobado
**Fecha:** 21 de agosto de 2026
**Total propuesto:** 35 productos en 7 categorÃ­as

## Criterios

- Los productos y precios son ficticios, pero representan artÃ­culos habituales de un minimarket peruano.
- `precio_venta_actual` se expresa en soles.
- `stock_actual` representa el inventario al cierre del 21/08/2026.
- `stock_minimo` es especÃ­fico para cada producto.
- Se incluyen intencionalmente productos agotados, crÃ­ticos, bajos y normales para demostrar las reglas de AgenteWasi.

## Productos propuestos

| ID | Producto | CategorÃ­a | Unidad | Precio S/ | Stock actual | Stock mÃ­nimo | Estado esperado |
|---|---|---|---|---:|---:|---:|---|
| PROD-001 | Arroz extra 1 kg | ABARROTES | BOLSA | 5.20 | 42 | 20 | NORMAL |
| PROD-002 | AzÃºcar rubia 1 kg | ABARROTES | BOLSA | 4.80 | 18 | 15 | BAJO |
| PROD-003 | Aceite vegetal 1 L | ABARROTES | BOTELLA | 10.90 | 9 | 12 | CRITICO |
| PROD-004 | Fideos spaghetti 500 g | ABARROTES | PAQUETE | 3.50 | 34 | 15 | NORMAL |
| PROD-005 | AtÃºn en lata 170 g | ABARROTES | LATA | 6.90 | 0 | 10 | AGOTADO |
| PROD-006 | Agua mineral 625 ml | BEBIDAS | BOTELLA | 2.00 | 55 | 20 | NORMAL |
| PROD-007 | Gaseosa cola 500 ml | BEBIDAS | BOTELLA | 3.50 | 21 | 15 | BAJO |
| PROD-008 | Gaseosa naranja 500 ml | BEBIDAS | BOTELLA | 3.20 | 14 | 12 | BAJO |
| PROD-009 | NÃ©ctar de durazno 1 L | BEBIDAS | CAJA | 5.90 | 6 | 8 | CRITICO |
| PROD-010 | Bebida rehidratante 500 ml | BEBIDAS | BOTELLA | 4.00 | 32 | 12 | NORMAL |
| PROD-011 | Leche evaporada 400 g | LACTEOS | LATA | 4.50 | 8 | 10 | CRITICO |
| PROD-012 | Yogur fresa 1 L | LACTEOS | BOTELLA | 7.90 | 16 | 12 | BAJO |
| PROD-013 | Yogur bebible 180 ml | LACTEOS | BOTELLA | 2.20 | 28 | 15 | NORMAL |
| PROD-014 | Queso fresco 250 g | LACTEOS | PAQUETE | 9.50 | 0 | 6 | AGOTADO |
| PROD-015 | Mantequilla 200 g | LACTEOS | PAQUETE | 8.90 | 8 | 8 | CRITICO |
| PROD-016 | Detergente 800 g | LIMPIEZA | BOLSA | 11.50 | 7 | 10 | CRITICO |
| PROD-017 | Lavavajilla 750 ml | LIMPIEZA | BOTELLA | 8.50 | 14 | 10 | BAJO |
| PROD-018 | LejÃ­a 1 L | LIMPIEZA | BOTELLA | 4.20 | 24 | 10 | NORMAL |
| PROD-019 | Papel higiÃ©nico 4 rollos | LIMPIEZA | PAQUETE | 8.90 | 18 | 12 | BAJO |
| PROD-020 | Limpiatodo 900 ml | LIMPIEZA | BOTELLA | 6.50 | 0 | 8 | AGOTADO |
| PROD-021 | ChampÃº 400 ml | CUIDADO_PERSONAL | BOTELLA | 14.90 | 5 | 7 | CRITICO |
| PROD-022 | JabÃ³n de tocador | CUIDADO_PERSONAL | UNIDAD | 3.20 | 27 | 12 | NORMAL |
| PROD-023 | Pasta dental 90 ml | CUIDADO_PERSONAL | UNIDAD | 7.50 | 13 | 10 | BAJO |
| PROD-024 | Desodorante 150 ml | CUIDADO_PERSONAL | UNIDAD | 12.90 | 18 | 8 | NORMAL |
| PROD-025 | Toallas higiÃ©nicas 10 unidades | CUIDADO_PERSONAL | PAQUETE | 8.20 | 0 | 8 | AGOTADO |
| PROD-026 | Galletas de vainilla | SNACKS | PAQUETE | 1.50 | 60 | 20 | NORMAL |
| PROD-027 | Papas fritas 45 g | SNACKS | BOLSA | 2.50 | 17 | 15 | BAJO |
| PROD-028 | Chocolate 30 g | SNACKS | UNIDAD | 2.00 | 10 | 10 | CRITICO |
| PROD-029 | Caramelos surtidos 100 g | SNACKS | BOLSA | 2.80 | 38 | 15 | NORMAL |
| PROD-030 | ManÃ­ salado 100 g | SNACKS | BOLSA | 3.50 | 0 | 8 | AGOTADO |
| PROD-031 | Pan francÃ©s | PANADERIA | UNIDAD | 0.40 | 85 | 30 | NORMAL |
| PROD-032 | Pan integral 500 g | PANADERIA | PAQUETE | 6.50 | 11 | 10 | BAJO |
| PROD-033 | Queque de vainilla 400 g | PANADERIA | PAQUETE | 9.90 | 5 | 6 | CRITICO |
| PROD-034 | Bizcochos 6 unidades | PANADERIA | PAQUETE | 4.50 | 22 | 10 | NORMAL |
| PROD-035 | Tostadas 200 g | PANADERIA | PAQUETE | 4.20 | 0 | 7 | AGOTADO |

## DistribuciÃ³n de estados propuesta

| Estado | Cantidad de productos |
|---|---:|
| AGOTADO | 6 |
| CRITICO | 8 |
| BAJO | 9 |
| NORMAL | 12 |
| Total | 35 |

## Validaciones previstas

- Los 35 identificadores serÃ¡n Ãºnicos.
- Todos los precios serÃ¡n mayores que cero.
- Todos los stocks serÃ¡n enteros no negativos.
- Todos los stocks mÃ­nimos serÃ¡n enteros mayores que cero.
- Todos los productos estarÃ¡n activos en la primera versiÃ³n.
- Las ventas solo utilizarÃ¡n productos incluidos en este catÃ¡logo.

## AprobaciÃ³n

El catÃ¡logo de 35 productos fue aprobado el 21 de agosto de 2026. Cualquier modificaciÃ³n posterior deberÃ¡ registrarse antes de regenerar la data.

### CorrecciÃ³n de coherencia previa a la generaciÃ³n

Antes de generar los CSV se corrigieron dos valores para que las filas coincidieran con la distribuciÃ³n de estados aprobada:

- `PROD-015` Mantequilla: `stock_actual` de 15 a 8; estado `CRITICO`.
- `PROD-019` Papel higiÃ©nico: `stock_actual` de 19 a 18; estado `BAJO`.

La distribuciÃ³n final validada es: 6 agotados, 8 crÃ­ticos, 9 bajos y 12 normales.
