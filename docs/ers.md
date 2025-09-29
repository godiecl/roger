# Especificación de Requerimientos del Sistema (ERS)
- **Propósito**: Definir los requerimientos funcionales y no funcionales del sistema.
- **Proyecto**: Plataforma Tecnológica para la Visibilización de Colecciones Patrimoniales.
## 1. Introducción
### 1.1 Propósito del Documento
El propósito de este documento es especificar los requerimientos de software para   el desarrollo del proyecto ROGER. Este ERS servirá como un acuerdo formal entre  el equipo de desarrollo y los stakeholders del proyecto, describiendo las funcionalidades,  características y restricciones que debe cumplir el sistema. Además, proporciona  una base para la planificación, ejecución y validación del proyecto, asegurando  que el producto final cumpla con las expectativas y objetivos establecidos en la  formulación del proyecto FONDEF.
### 1.2 Público Objetivo
Este documento está dirigido a:
1. Público General.
2. Curadores y Expertos del proyecto.
3. Administradores del sistema
4. Equipo de desarrollo de software.
### 1.3 Alcance del Sistema
La plataforma tecnológica considera como principales componentes según el documento FONDEF los siguientes módulos:
1. **Digitalización de la colección**: Este módulo se encargará de la digitalización y catalogación de los negativos y fotografías históricas.
2. **Procesamiento de imágenes**: centrado en el análisis y mejora de las imágenes digitalizadas.
3. **Procesamiento de textos**: responsable de la generación y análisis de descripciones textuales de las imágenes.
4. **Captura del conocimiento**: En este módulo se integra la información visual y textual.
5. **Administración del conocimiento**: encargado de gestionar la información y el conocimiento generado a partir del análisis de las colecciones.
6. **Generación de nuevo conocimiento**: creación de nuevas narrativas y conexiones entre las colecciones analizadas.

El sistema permitirá:
1. Acceder y visualizar la colección de fotografías digitalizadas.
2. Filtrar y buscar imágenes por metadatos (autor, año, ubicación, palabra clave).
3. Generar narrativas y líneas de tiempo a partir de las imágenes utilizando inteligencia artificial.
4. Visualizar la ubicación de las fotos en sus estantes mediante una biblioteca virtual interactiva.
5. Proporcionar métricas de certeza o confianza en los resultados factuales.
6. Permitir la colaboración en sesiones multiusuario con historial de consultas.
7. Reconocer objetos y personas dentro de las imágenes digitalizadas.
8. Guardar nuevo conocimiento generado.
9. Gestionar roles y permisos para el acceso a las herramientas de curación y administración.
10. Descargar el contenido (imágenes y narrativas generadas).
## 2. Descripción General del Sistema
### 2.1 Contexto
El proyecto ROGER es una iniciativa financiada por FONDEF, con la Universidad Católica del Norte (UCN) como entidad beneficiaria y la Corporación Cultural de Antofagasta como entidad asociada. El objetivo principal es desarrollar una plataforma web que, mediante el uso de inteligencia artificial generativa, permita procesar una colección patrimonial de imágenes históricas para generar narrativas y conocimiento a partir de ellas. La plataforma busca rescatar y poner en valor el archivo fotográfico de Robert Gerstmann.
### 2.2 Objetivos generales del sistema
El sistema busca dar soporte tecnológico al proceso de visibilización y puesta en valor del archivo Gerstmann. Sus principales objetivos son:
1. Proporcionar una plataforma pública para la exploración de la colección fotográfica.
2. Facilitar la búsqueda y el acceso a la información a través de filtros y metadatos.
3. Automatizar la generación de narrativas para agilizar el proceso de curación y análisis.
4. Ofrecer herramientas de curación y administración a los usuarios especializados.
5. Mejorar la trazabilidad y el control de las acciones realizadas sobre el contenido.
6. Asegurar la compatibilidad e integración con las tecnologías de IA generativa.
7. Minimizar los errores humanos en la manipulación y clasificación del material.
### 2.3 Actores Principales
Los actores principales del sistema son:

| Actor             | Descripción                                                                                            |
| ----------------- | ------------------------------------------------------------------------------------------------------ |
| Usuario           | Cualquier persona que accede a la plataforma para visualizar y explorar el contenido público.          |
| Curador / Experto | Persona responsable de validar, aportar metadatos y moderar las narrativas y la información histórica. |
| Administrador     | Persona encargada de gestionar los usuarios, los roles y la configuración general de la plataforma.    |
| Sistema IA        | Componente de inteligencia artificial que procesa las imágenes y genera las narrativas.                |

### 2.4 Suposiciones y dependencias
- **Suposiciones**: Se asume que el archivo fotográfico de Robert Gerstmann ya tiene parte de las fotografías digitalizadas y disponible en un repositorio al cual la plataforma tendrá acceso.
- **Dependencias**: El proyecto depende de la disponibilidad y el correcto funcionamiento de los modelos de inteligencia artificial y del desarrollo de las APIs para la generación de narrativas. La participación de los curadores y expertos es crucial para la validación y el enriquecimiento de la información.
### 2.5 Indicadores cuantitativos y cualitativos
El proyecto va a ser medido de manera cualitativa y cuantitativa con los siguientes indicadores:
#### Cualitativos:
1. ICa1: porcentaje de similaridad entre anotaciones y descripciones narrativas generadas por inteligencia artificial versus generadas por humanos con expertiz en el dominio de la colección patrimonial.
2. ICa2: nivel de consistencia entre las relaciones entre objetos de la colección identificadas por las herramientas de inteligencia artificial de forma automática, evaluada según juicio humano experto.
3. ICa3: nivel de consistencia entre las líneas de tiempo propuesta por la aplicación de LLMs sobre los objetos componentes de la colección patrimonial, y las propuestas realizadas en base a juicio humano experto en el dominio.
4. ICa4: porcentaje de implementación de la estructura modular propuesta en el proyecto.
#### Cuantitativos:
1. ICl1: nivel de satisfacción de los usuarios finales con respecto a la funcionalidad del sistema desarrollada
2. ICl2: nivel de satisfacción de los expertos en el dominio del problema (colección patrimonial) con respecto a la coherencia de las descripciones narrativas generadas por las componentes de inteligencia artificial generativa.
3. ICl3: nivel de satisfacción de los usuarios finales, administradores del conocimiento y expertos del dominio del problema, con respecto a la usabilidad de las distintas funcionalidades implementadas por la plataforma tecnológica inteligente.
## 3. Requerimientos Funcionales (RF)
Los requerimientos funcionales especifican lo que el sistema debe hacer para cumplir con las necesidades del proyecto.
### 3.1. Visualización de Contenido Patrimonial (RF-01)
El sistema debe permitir a los usuarios visualizar imágenes individuales y en grupos (clusters).
El sistema debe permitir crear líneas de tiempo del recorrido de Robert Gerstmann.
### 3.2. Funcionalidades de Búsqueda y Filtrado (RF-02)
El sistema debe permitir a los usuarios buscar y filtrar imágenes por palabras clave, año y ubicación.
Debe integrar herramientas de búsqueda que permitan a los usuarios localizar contenido de manera eficiente.
### 3.3. Generación de Narrativas (RF-03)
El sistema debe ser capaz de generar narrativas a partir de las imágenes.
Debe permitir la creación de narrativas visuales y líneas de tiempo coherentes, apoyadas por inteligencia artificial.
Se debe incorporar el conocimiento experto humano en la generación de narrativas para asegurar la coherencia y consistencia.
### 3.4. Gestión de Contenido (RF-04)
Los Curadores y Administradores deben poder aportar metadatos y validar la información relacionada con las imágenes.
El sistema debe permitir a los Curadores y Administradores gestionar/modificar descripciones realizadas por la IA.
El sistema debe permitir a los Curadores y Administradores agregar meta data a las fotografías.
### 3.5. Descarga de Archivos (RF-05)
El sistema debe permitir la descarga de imágenes y los textos generados.
### 3.6. Visita Virtual a la Biblioteca (RF-06)
El sistema debe contar con una funcionalidad que muestre la ubicación virtual de las fotos en sus estantes dentro de la biblioteca, ofreciendo una experiencia interactiva.
## 4. Requerimientos No Funcionales (RNF)
Los requerimientos no funcionales definen las características de calidad y las restricciones de operación del sistema.
### 4.1. Seguridad y Autenticación (RNF-01)
- El sistema debe implementar un control de acceso basado en roles para diferenciar las funcionalidades disponibles para Usuarios Estándar, Curadores / Expertos y Administradores.
- La funcionalidad de creación y validación de narrativas debe estar restringida exclusivamente a los roles de Curador / Experto y Administrador.
### 4.2. Usabilidad (RNF-02)
- La interfaz de usuario debe ser intuitiva y fácil de usar, con una curva de aprendizaje mínima para los Usuarios Estándar.
- La interfaz además debe cumplir con estándares de usabilidad y accesibilidad (WCAG 2.1, ISO 9241-210).
### 4.3. Escalabilidad y Rendimiento (RNF-03)
- La plataforma debe ser capaz de manejar un gran volumen de imágenes sin comprometer el rendimiento.
- El sistema debe responder de manera rápida a las interacciones del usuario.
- El sistema debe tener la capacidad de trabajar con otros conjuntos de datos además del inicial.
### 4.4. Mantenibilidad y Extensibilidad (RNF-04)
- El sistema debe contar con la documentación pertinente y el código fuente comentado para facilitar su mantenimiento y futuras actualizaciones.
- Debe ser posible integrar nuevos modelos de inteligencia artificial o de procesamiento de imágenes.
### 4.5. Disponibilidad y Confiabilidad (RNF-05)
- El sistema debe estar disponible las 24 horas del día, los 7 días de la semana, con un tiempo de inactividad mínimo programado.
- El sistema debe ser resiliente a fallas y recuperar la información de manera segura.
### 4.6. Eficiencia de Costos (RNF-06)
- Para minimizar los costos de tokenización y optimizar el rendimiento, el sistema debe utilizar un mecanismo de caché para las narrativas e imágenes generadas.
- El acceso a la generación de nuevas narrativas y a la retroalimentación del modelo de IA debe estar estrictamente controlado y limitado a los roles de Curador / Experto y Administrador, evitando así el uso indiscriminado por parte de los Usuarios Estándar.
### 4.7. Cumplimiento Normativo (RNF-07)
- El sistema debe cumplir con las normas gráficas de la Universidad Católica del Norte (UCN) y las directrices de uso de logos de las entidades financistas (ANID y Ministerio de Ciencia).
- Debe cumplir con las normativas de preservación digital (ISO 19263-1:2017, ISO 15836-1:2017) y de protección de datos personales (Ley 19.628 en Chile).
## 5 Requerimientos Técnicos (RT)
Los requerimientos técnicos especifican la infraestructura, las herramientas y las tecnologías necesarias para el desarrollo y despliegue del sistema. Estos requisitos se han definido considerando la naturaleza del proyecto FONDEF y los módulos tecnológicos propuestos.
### 5.1. Arquitectura de Software
La plataforma debe tener una arquitectura modular que permita la integración de nuevas funcionalidades sin afectar las existentes.
La estructura principal incluye:
- **Módulo de Acceso y Visualización**: Para la interfaz de usuario que permite la navegación y la interacción con la colección digitalizada.
- **Módulo de Gestión de Contenido**: Para la base de datos que almacena metadatos, los roles de usuario y las herramientas de administración y curación, incluyendo el almacenamiento de las imágenes y narrativas generadas.
- **Módulo de Inteligencia Artificial**: Para el procesamiento de las imágenes y la generación de narrativas y contenido visual, que se conecta con modelos externos de IA.
### 5.2. Generación de Imágenes
- El sistema debe ser capaz de generar nuevas imágenes a partir de descripciones textuales o de combinaciones de imágenes existentes, como parte del proceso de creación de narrativas o para enriquecer los clusters.
- El contenido visual generado por la IA debe ser gestionado y almacenado de manera segura en el sistema, al igual que las imágenes patrimoniales.
- Se requerirá un sistema de moderación por parte de los Curadores y Expertos para la aprobación del contenido generado antes de su publicación.
### Bibliografía
- TODO: Agregar bibliografía.
