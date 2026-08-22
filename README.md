# AgenteWasi

Agente inteligente desarrollado con Python y Microsoft Foundry para apoyar al propietario de un minimarket en el análisis de ventas, inventario e indicadores de clientes ficticios.

## Objetivo

Permitir consultas en lenguaje natural sobre archivos CSV y responder con resultados calculados mediante herramientas Python, sin inventar información ni modificar los datos originales.

## Funcionalidades previstas

- Calcular ventas por día o periodo.
- Identificar productos más vendidos.
- Identificar productos que generan mayores ingresos.
- Detectar productos agotados, críticos o con stock bajo.
- Recomendar cantidades informativas de reposición.
- Analizar ventas por categoría.
- Detectar productos con poca o ninguna venta.
- Identificar clientes ficticios con más compras y mayor gasto.
- Calcular el ticket promedio y el porcentaje de clientes recurrentes.
- Informar errores cuando los archivos o columnas sean inválidos.

## Tecnologías

- Python 3.12
- Microsoft Foundry
- Azure OpenAI
- Modelo `gpt-4.1-mini`
- Deployment `agentewasi-gpt41-mini`
- Azure AI Projects
- OpenAI SDK
- pandas
- pytest

## Estructura del proyecto

```text
AgenteWasi/
|-- data/           # Archivos CSV ficticios
|-- docs/           # Documentación del proyecto
|-- scripts/        # Scripts auxiliares
|-- src/            # Código fuente
|-- tests/          # Pruebas automatizadas
|-- .env.example    # Plantilla de configuración
|-- .gitignore
|-- LICENSE
|-- README.md
`-- requirements.txt

```

## Requisitos

- Python 3.12
- Git
- Acceso a Microsoft Foundry
- Una implementación compatible de Azure OpenAI

## Instalación en Windows

1. Clonar el repositorio:
   git clone https://github.com/manayaycastro/AgenteWasi.git

2. Ingresar al proyecto:
   Set-Location "AgenteWasi"

3. Crear el entorno virtual:
   py -3.12 -m venv .venv

4. Activar el entorno virtual:
   .\.venv\Scripts\Activate.ps1

5. Instalar y verificar las dependencias:
   python -m pip install -r requirements.txt
   python -m pip check

## Configuración

Crear el archivo local `.env` tomando como referencia `.env.example`.

El archivo `.env` contiene información sensible y está excluido mediante `.gitignore`. Nunca se deben publicar claves ni endpoints reales.

## Datos

El proyecto utiliza datos ficticios de un minimarket correspondientes a 2026, hasta el 21 de agosto de 2026.

Archivos definidos:

- `data/ventas_ejemplo.csv`
- `data/inventario_ejemplo.csv`
- `data/datos_invalidos_columnas.csv`
- `docs/diccionario_datos.md`
- `docs/resumen_data.md`

Los códigos y nombres de clientes son ficticios. No se emplean datos personales reales.

## Estado del proyecto

Actualmente cuenta con herramientas Python, integración con Microsoft Foundry, interfaz CLI y 102 pruebas automatizadas aprobadas.

Se completó la configuración del repositorio, Python, entorno virtual, dependencias, Microsoft Foundry, variables de entorno y licencia.

Las siguientes etapas corresponden a la revisión final del repositorio y la preparación del video demostrativo.

## Limitaciones

AgenteWasi no realizará predicciones mediante aprendizaje automático, operaciones contables, asesoría legal o tributaria, pedidos automáticos ni modificaciones directas de ventas o inventario.

## Licencia

Este proyecto utiliza la licencia MIT. Consulta el archivo `LICENSE`.

## Ejecución

Activar el entorno virtual:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instalar el proyecto en modo editable:

```powershell
python -m pip install -e .
```

Ejecutar la suite automatizada:

```powershell
python -m pytest -q
```

Iniciar AgenteWasi:

```powershell
python -m agentewasi
```

Para finalizar la conversación, escribir `salir`.

## Preguntas de ejemplo

- ¿Cuánto se vendió el 21 de agosto de 2026?
- ¿Cuáles fueron los cinco productos más vendidos?
- ¿Qué productos tienen stock crítico?
- ¿Qué productos debo reponer?
- ¿Qué categorías generaron mayores ventas?
- ¿Quiénes son los clientes con más compras?

## Documentación

- [Arquitectura y flujo](docs/arquitectura.md)
- [Matriz de pruebas](docs/pruebas.md)
- [Seguridad, límites y costos](docs/seguridad_limites_costos.md)
- [Diccionario de datos](docs/diccionario_datos.md)
- [Ficha del proyecto](docs/ficha_proyecto.md)
