E-commerce Chat AI — FastAPI · SQLAlchemy · Gemini · Docker

API de e-commerce (catálogo de zapatillas) con un asistente conversacional basado en Google Gemini.
Incluye arquitectura en capas, documentación con docstrings en español (estilo Google), pruebas unitarias con pytest y cobertura, y despliegue local y con Docker.

Descripción del proyecto

Este proyecto implementa un backend de catálogo de productos (zapatillas) y un endpoint de chat que genera respuestas contextuales combinando el historial de la conversación y el catálogo disponible, mediante el proveedor de IA Google Generative AI (Gemini).

La API se publica con FastAPI (documentación Swagger en /docs) y persiste datos con SQLite vía SQLAlchemy. Para facilitar la ejecución, se entrega con Dockerfile y docker-compose.

Características principales

Catálogo de productos (consulta por lista e ID).

Chat con IA (Gemini) utilizando contexto e inventario.

Arquitectura en capas (domain / application / infrastructure).

SQLite + SQLAlchemy, modelos ORM y repositorios concretos.

Documentación automática con Swagger/OpenAPI.

Testing con pytest y cobertura con pytest-cov.

Contenedorización con Docker y orquestación con docker-compose.

Docstrings en español (estilo Google) en clases, funciones y endpoints.

Arquitectura (diagrama)

Separación en tres capas:

domain/: Entidades, interfaces de repositorios, excepciones (lógica de negocio pura).

application/: Servicios/casos de uso que orquestan repositorios y proveedor de IA.

infrastructure/: Exposición HTTP (FastAPI), implementación SQLAlchemy, proveedor Gemini y scripts de inicialización.

Instalación (entorno local)
# 1) Clonar
git clone <URL_DEL_REPOSITORIO>
cd e-commerce-chat-ai

# 2) Crear entorno virtual (Windows)
python -m venv venv
venv\Scripts\activate

# 3) Instalar dependencias
python -m pip install --upgrade pip
pip install -r requirements.txt

Configuración

Crear el archivo .env (puede basarse en .env.example) con al menos:

GEMINI_API_KEY=AIza...                  # clave real de Google AI Studio
# GEMINI_MODEL=gemini-2.5-flash         # opcional (por defecto se usa 2.5-flash)
DATABASE_URL=sqlite:///./data/ecommerce_chat.db
ENVIRONMENT=development


No subir .env al repositorio. Documentar variables en .env.example.

Uso (ejemplos de endpoints)

Inicializar datos (crea tablas e inserta 10 productos si no existen):

python -m src.infrastructure.db.init_data


Levantar la API:

uvicorn src.infrastructure.api.main:app --reload


Probar endpoints:

Documentación Swagger: http://localhost:8000/docs

Health: GET http://localhost:8000/health

Productos:

GET /products

GET /products/{id}

Chat:

POST /chat
Ejemplo de cuerpo:

{
  "session_id": "u1",
  "message": "Busco zapatos para correr talla 42"
}


Historial:

GET /chat/history/{session_id}?limit=10

DELETE /chat/history/{session_id}

Uso por consola (guía rápida)

En Windows CMD:

set BASE=http://localhost:8000

:: ver estado
curl %BASE%/
curl %BASE%/health

:: productos
curl %BASE%/products
curl %BASE%/products/1
curl -i %BASE%/products/99999

:: chat (primer mensaje y seguimiento)
curl -X POST %BASE%/chat -H "Content-Type: application/json" -d "{\"session_id\":\"u1\",\"message\":\"Busco zapatos para correr talla 42\"}"
curl -X POST %BASE%/chat -H "Content-Type: application/json" -d "{\"session_id\":\"u1\",\"message\":\"Prefiero marca Nike y color negro\"}"

:: historial
curl %BASE%/chat/history/u1
curl "%BASE%/chat/history/u1?limit=1"
curl -X DELETE %BASE%/chat/history/u1

Testing

Ejecutar pruebas:

pytest


Con cobertura (reporte en consola):

pytest --cov=src --cov-report=term-missing


Reporte HTML:

pytest --cov=src --cov-report=html


Abrir htmlcov/index.html en el navegador.

Docker

Archivos relevantes: Dockerfile, docker-compose.yml, .dockerignore.

Construir e iniciar:

docker compose build --no-cache
docker compose up -d


Inicializar datos dentro del contenedor:

docker compose exec api python -m src.infrastructure.db.init_data


Verificación:

Swagger: http://localhost:8000/docs

Logs: docker compose logs -f api

Contenedores activos: docker ps

Notas:

docker-compose.yml monta ./data en /app/data para persistir la base de datos en el host.

La variable GEMINI_API_KEY se toma desde el .env del host.

Tecnologías utilizadas

FastAPI, Uvicorn

SQLAlchemy (SQLite)

Pydantic v2

Google Generative AI (Gemini)

Pytest, pytest-cov

Docker, docker-compose

Estructura del proyecto
src/
  domain/
    entities.py               # Entidades (Product, ChatMessage, ChatContext)
    exceptions.py             # Excepciones de dominio
    repositories.py           # Interfaces de repositorios
  application/
    product_service.py        # Lógica de catálogo
    chat_service.py           # Orquestación del chat con IA
    dtos.py                   # DTOs de entrada/salida
  infrastructure/
    api/main.py               # FastAPI: endpoints y startup
    db/
      database.py             # Engine, sesión y Base
      models.py               # Modelos ORM
      init_data.py            # Carga de 10 productos si está vacío
    repositories/
      product_repository.py   # Repo SQLAlchemy de productos
      chat_repository.py      # Repo SQLAlchemy de historial
    llm_providers/
      gemini_service.py       # Adaptador de Gemini (GenerativeModel)
tests/
  test_entities.py
  test_services.py
  ...
evidencias/
  01-swagger-ui.png
  02-docker-logs.png
  03-docker-running.png
  04-api-call-products.png
  05-api-call-chat.png
  06-database.png

  test corto:

  :: 0) levantar todo y preparar
docker compose up -d
docker compose exec api python -m src.infrastructure.db.init_data

:: 1) variable base
set BASE=http://localhost:8000

:: 2) healthcheck y raíz
curl %BASE%/health
curl %BASE%/

:: 3) productos: lista e ID válido/ inválido
curl %BASE%/products
curl %BASE%/products/1
curl -i %BASE%/products/99999

:: 4) chat: primer mensaje
curl -X POST %BASE%/chat -H "Content-Type: application/json" ^
 -d "{\"session_id\":\"u1\",\"message\":\"Busco zapatos para correr talla 42\"}"

:: 5) chat: seguimiento en misma sesión
curl -X POST %BASE%/chat -H "Content-Type: application/json" ^
 -d "{\"session_id\":\"u1\",\"message\":\"Prefiero marca Nike y color negro\"}"

:: 6) historial: leer últimos 2
curl "%BASE%/chat/history/u1?limit=2"

:: 7) historial: borrar
curl -X DELETE %BASE%/chat/history/u1
curl "%BASE%/chat/history/u1?limit=10"