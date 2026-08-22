# Guion del video demostrativo de AgenteWasi

**Duración máxima:** 3 minutos
**Formato:** narración y grabación de pantalla

## 0:00-0:20 — Problema

**Pantalla:** README del repositorio.

**Narración:**
“Un propietario de minimarket registra ventas e inventario, pero revisar manualmente miles de registros dificulta conocer ingresos, productos destacados y existencias críticas. Para resolver este problema desarrollé AgenteWasi.”

## 0:20-0:45 — Solución

**Pantalla:** descripción y funcionalidades del README.

**Narración:**
“AgenteWasi es un agente desarrollado con Python y Microsoft Foundry. Analiza archivos CSV ficticios, calcula indicadores verificables y responde preguntas en lenguaje natural sin inventar cifras ni modificar los datos.”

## 0:45-1:10 — Arquitectura

**Pantalla:** `docs/arquitectura.md` mostrando el diagrama.

**Narración:**
“El usuario consulta mediante una interfaz de línea de comandos. El modelo gpt-4.1-mini interpreta la pregunta y selecciona una herramienta. Python valida los CSV, realiza el cálculo y devuelve un resultado estructurado para que el modelo redacte la respuesta.”

## 1:10-2:10 — Demostración funcional

**Pantalla:** PowerShell con el entorno virtual activo.

Ejecutar:

```powershell
python -m agentewasi```

Primera pregunta:

```text
¿Cuánto se vendió el 21 de agosto de 2026?
```

**Narración breve:**
“El resultado se calcula directamente desde el archivo de ventas.”

Segunda pregunta:

```text
¿Qué productos tienen stock crítico?
```

**Narración breve:**
“El agente consulta el inventario y clasifica productos agotados, críticos y con stock bajo.”

## 2:10-2:35 — Límite controlado

Pregunta:

```text
¿Puedes predecir las ventas del próximo año?
```

**Narración:**
“AgenteWasi rechaza consultas fuera de alcance. No realiza predicciones ni presenta información que no esté respaldada por sus herramientas.”

## 2:35-2:55 — Calidad y aprendizaje

**Pantalla:** `docs/pruebas.md` o salida de pytest.

**Narración:**
“El proyecto cuenta con 102 pruebas automatizadas, validación de datos, manejo de errores externos y protección de credenciales mediante variables de entorno.”

## 2:55-3:00 — Cierre

**Pantalla:** repositorio GitHub.

**Narración:**
“AgenteWasi integra un modelo con herramientas Python para resolver una necesidad comercial concreta de manera segura y verificable.”

## Preparación antes de grabar

- Activar `.venv`.
- Comprobar la conexión con Azure.
- Abrir README, arquitectura y pruebas.
- Aumentar el tamaño de fuente de PowerShell.
- Ocultar `.env`, claves, endpoints y notificaciones.
- Probar previamente las preguntas.
- Escribir `salir` al terminar.
- Mantener la grabación por debajo de tres minutos.
