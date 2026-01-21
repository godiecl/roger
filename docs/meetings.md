# The Meetings

--- 

## 2026.01.15 Reunión de planificación del proyecto

- **Asistentes**: dleon, bmuñoz, durrutia.
- **Horario**: 15:45 - 17:30.
- **Actividades a realizar**:
    - [X] Definir la plataforma tecnológica a utilizar en Leila.
    - [X] Definir la plataforma tecnológica a utilizar en Valeria.
    - [X] Establecer el cronograma para el desarrollo de las funcionalidades principales.

### Definir la plataforma tecnológica a utilizar en Leila

- **Tecnologías analizadas en frontend (Leila)**:
    - **Javascript frameworks**: [SolidJS](https://www.solidjs.com/), [NextJS](https://nextjs.org/), [Svelte](https://qwik.dev/), [Qwik](https://qwik.dev/).
      - En la revisión de estos frameworks, se consideraron aspectos como el rendimiento, la 
        facilidad de uso, la comunidad y la escalabilidad.
      - El equipo discutió las ventajas y desventajas de cada opción, evaluando cómo se alineaban con los 
        objetivos del proyecto Leila y se tomó la decisión de utilizar **Svelte** debido a su simplicidad y eficiencia.
    - **Lenguajes de programación**: [Svelte Typescript](https://svelte.dev/docs/svelte/typescript).
    - **CSS Frameworks**: [daisyUI](https://daisyui.com/).
      - Se evaluaron varios frameworks de CSS, incluyendo Tailwind CSS, Bootstrap y Bulma. Se 
        decidió seleccionar **daisyUI** por su integración fluida con Tailwind CSS y su capacidad para
        facilitar el desarrollo de interfaces de usuario atractivas y responsivas bajo el 
        framework Svelte.
- **Tecnologías analizadas en backend (Valeria)**:
    - **Frameworks**: [Django](https://www.djangoproject.com/), [Flask](https://flask.palletsprojects.com/en/2.3.x/), [FastAPI](https://fastapi.tiangolo.com/).
      - Se consideraron varios frameworks de backend, evaluando factores como la facilidad de 
        desarrollo, el rendimiento y la comunidad. Finalmente, se optó por **FastAPI** debido a su 
        rendimiento superior y su capacidad para manejar aplicaciones asíncronas de manera eficiente.
    - **Lenguajes de programación**: [Python 3.x+](https://www.python.org).
      - Se decidió utilizar Python 3.x+ como lenguaje de programación principal para el backend,
        aprovechando su amplia adopción en la comunidad de desarrollo y su compatibilidad con FastAPI.
      - La versión específica de Python se determinará en función de la compatibilidad con las 
        bibliotecas y dependencias necesarias para el proyecto.
    - **Bases de datos**: [PostgreSQL](https://www.postgresql.org/), [MySQL](https://www.mysql.com/), [SQLite](https://www.sqlite.org/index.html).
      - Se evaluaron varias opciones de bases de datos, considerando factores como el rendimiento, la 
        escalabilidad y la facilidad de uso. Se decidió utilizar **SQLite** debido a su simplicidad y 
        facilidad de configuración para el _desarrollo inicial del proyecto_.
    - **ORMs**: [SQLAlchemy](https://www.sqlalchemy.org/), [Tortoise ORM](https://tortoise-orm.readthedocs.io/en/latest/), [SQLModel](https://sqlmodel.tiangolo.com/).
      - Se analizaron diferentes opciones de ORM para facilitar la interacción con la base de datos. 
        Finalmente, se optó por **SQLModel** debido a su flexibilidad y amplia adopción en la comunidad de desarrollo Python.

### Establecer el cronograma para el desarrollo de las funcionalidades principales

- Se discutió la revisión de los distintos requerimientos funcionales y no funcionales del proyecto. A partir de ello, se decidió planificar la construcción en distintas etapas, priorizando aquellas funcionalidades que son críticas para el lanzamiento inicial del proyecto.

- **Etapa 1**: Desarrollo de funcionalidades críticas (Enero 2026 -> Marzo 2026).
    1. **RNF-01**: Seguridad y Autenticación.
    2. **RF-01**: Visualización de Contenido Patrimonial.
    3. **RF-13**: Visibilidad de Colecciones.
    4. **RF-02**: Funcionalidades de Búsqueda y Filtrado.
    5. **RF-05**: Descarga de Archivos.
- **Etapa 2**: Desarrollo de funcionalidades secundarias (Marzo 2026 -> ).
    1. **RF-04**: Gestión de Contenido.
    2. **RF-07**: Etiquetado temático.
    3. **RF-10**: Grupos de Proyectos.
    4. **RF-06**: Ubicación por lugares y zonas.
    5. **RF-09**: Georreferenciación y mapa.
- **Etapa 3**: Integración y pruebas finales (Junio 2026 -> Julio 2026).
    1. **RF-08**: Líneas de tiempo paralelas.
    2. **RF-03**: Generación de Narrativas.
    3. **RF-11**: Análisis IA con trazabilidad.
    4. **RF-12**: Contribuciones de usuarios registrados.
    5. **RF-14**: Comparador histórico "Antes/Ahora".
