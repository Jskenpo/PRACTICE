# Preparación para entrevista técnica de backend con FastAPI

## Contexto

El ejercicio técnico será un backend con conexión a base de datos. Se permite usar IA, pero hay que poder explicar **qué hace el código, cómo funciona y por qué se eligió cada solución**. El objetivo de esta conversación fue repasar conceptos y detectar puntos que conviene practicar antes del ejercicio.

## Docker y contenedores

- **Dockerfile:** receta que define cómo construir el entorno de la aplicación.
- **Imagen:** resultado de construir esa receta.
- **Contenedor:** instancia en ejecución de una imagen.
- **Docker Compose:** describe y levanta varios servicios relacionados.

En un backend FastAPI, una composición posible incluye la API, PostgreSQL y, solo si se necesitan tareas en cola o caché, Redis y un worker. La API y el worker pueden partir de la misma imagen de Python y ejecutar comandos distintos. La base de datos necesita un volumen para conservar datos cuando se recrea el contenedor. Dentro de la red de Compose, los servicios se comunican por su nombre de servicio.

**Idea para explicar:** Docker hace reproducible el entorno; Compose describe cómo colaboran sus procesos.

## Redis y tareas en segundo plano

Redis es un almacén de datos rápido, usado habitualmente para caché, datos temporales, límites de uso y como intermediario de mensajes para colas. No es obligatorio en toda API. Si una consulta es lenta, primero hay que revisar la consulta y sus índices antes de añadir caché.

En una cola con **FastAPI + Celery + Redis**:

1. FastAPI recibe la solicitud y envía una tarea a la cola.
2. Redis actúa como *broker* y mantiene el mensaje pendiente.
3. Un worker de Celery toma la tarea y la ejecuta fuera del proceso que atiende HTTP.

**Celery Beat** programa tareas periódicas; los workers las ejecutan. Un cron job también puede lanzar tareas a horas determinadas. **Flower** permite observar workers y tareas. **Horizon pertenece a Laravel** y no forma parte de FastAPI.

FastAPI ofrece `BackgroundTasks` para trabajos sencillos dentro del proceso de la aplicación. Una cola con workers separados sirve cuando el trabajo es más pesado o necesita ejecutarse independientemente. Para tareas que pueden reintentarse, conviene diseñarlas de forma **idempotente**: ejecutarlas dos veces no debe producir efectos indebidos, como cobrar dos veces una orden.

## Seguridad de una API

Cada mecanismo responde una pregunta distinta:

| Mecanismo | Función principal |
| --- | --- |
| Load balancer o proxy | Recibir y distribuir tráfico; puede terminar HTTPS. |
| API Gateway | Centralizar rutas, límites de uso y algunas reglas de acceso. |
| API key | Identificar la aplicación o sistema cliente, cuando aplica. |
| JWT | Autenticar al usuario que hace la petición. |
| Rol | Autorizar un tipo de operación. |
| Autorización por recurso | Comprobar acceso al registro específico solicitado. |
| CORS | Indicar a los navegadores qué orígenes pueden leer respuestas. |

Un JWT válido y un rol permitido no bastan para devolver cualquier registro. Si un cliente puede consultar pedidos, `GET /orders/42` debe comprobar que el pedido 42 le pertenece o que tiene un permiso explícito para verlo. Conviene aplicar el alcance directamente en la consulta, por ejemplo filtrando por `order_id` y `user_id` autenticado. En esta conversación llamamos a esto **autorización a nivel de recurso** o **alcance de datos**; no debe confundirse con los *scopes* de OAuth.

La API key y el JWT pueden utilizarse juntos cuando interesa identificar tanto la aplicación cliente como al usuario. Una API key incluida en un navegador o una app móvil puede extraerse, por lo que no debe considerarse un secreto fuerte. CORS controla el comportamiento del navegador; no autentica las solicitudes.

Al validar un JWT hay que verificar la firma, el algoritmo esperado, la expiración y los datos de emisión o audiencia que exija el sistema. Su contenido está firmado, no cifrado. Para contraseñas se usa un hash adecuado. Las consultas SQL deben ser parametrizadas o construidas con un ORM, y los secretos de configuración deben mantenerse fuera del código.

**Frase útil para la entrevista:** «Identifico al cliente con API key cuando aplica; autentico al usuario con JWT; verifico su rol para la operación; y compruebo que tenga acceso al recurso concreto».

## Clean code y optimización

Un endpoint debería permitir seguir fácilmente este recorrido:

```text
Petición → validación → autenticación y autorización → regla de negocio
         → base de datos → respuesta definida
```

Para un ejercicio corto, la organización debe ayudar a entender el código sin crear capas vacías. Conviene usar nombres claros, separar los modelos de entrada y salida de los modelos de base de datos y devolver solo los campos necesarios. Un `response_model` de FastAPI puede definir y filtrar la salida.

Antes de optimizar, hay que encontrar el costo real. En APIs con base de datos, revisar especialmente:

- **Paginación** y orden estable para listas grandes.
- **Índices** acordes a los filtros y al orden de las consultas frecuentes.
- **Consultas N+1**, cuando se ejecuta otra consulta por cada registro de una lista.
- **Volumen de datos devueltos** y campos realmente necesarios.
- **Plan de ejecución** y tiempos de consulta, por ejemplo con `EXPLAIN` en PostgreSQL.

Para evaluar código generado por IA, preguntar: ¿qué recibe y devuelve?, ¿quién puede usarlo y sobre qué datos?, ¿qué consultas realiza?, ¿qué pasa si falla a mitad?, ¿qué ocurre con listas vacías, IDs inexistentes, datos inválidos y muchos registros?

## Diseño de base de datos: ejemplo de pedidos

Se planteó un sistema con usuarios, pedidos y productos. La propuesta inicial fue `users`, `orders`, `products` y una tabla intermedia porque un pedido contiene muchos productos y un producto puede aparecer en muchos pedidos. Esa relación es correcta. La tabla intermedia puede llamarse `order_items` y debe guardar, como mínimo:

```text
order_id | product_id | quantity | unit_price
```

`unit_price` representa el **precio histórico de la venta**. El precio actual pertenece a `products`, pero cambiarlo mañana no debe modificar el importe de un pedido anterior. Se discutió el uso de UUID v4 para IDs: es una opción válida, junto con claves primarias y restricciones de unicidad en la base de datos. Un ID difícil de adivinar no sustituye la autorización.

La experiencia en restaurantes llevó a proponer tablas para movimientos de inventario, saldo y recetas. Es un diseño razonable para ese dominio; hay que precisar cuál es la fuente de verdad del saldo y evitar registrar dos veces un descuento. También conviene definir restricciones como `quantity > 0` y usar tipos decimales adecuados para dinero.

### Transacciones

Al crear un pedido, el encabezado, las líneas, los movimientos y el descuento de inventario deben formar una **operación completa**. Si falla la tercera línea, se revierte todo lo anterior. La decisión operativa posterior puede ser avisar al usuario, deshabilitar el producto problemático y permitir rehacer el pedido. La transacción protege los datos durante el intento fallido.

### Concurrencia e inventario negativo

Permitir inventario negativo puede ser una regla de negocio válida si el saldo del restaurante es aproximado. Partiendo de 2 unidades, dos ventas simultáneas de 2 deben dejar saldo **−2** y generar **dos movimientos de −2**.

Si ambas solicitudes leen `2` y cada una calcula `0` en Python para luego guardarlo, una puede sobrescribir el efecto de la otra: es una **actualización perdida**. Para evitarlo, el descuento debe aplicarse de forma coordinada en la base de datos, dentro de la transacción; por ejemplo, con una actualización `stock = stock - cantidad`. Si el negocio prohíbe vender sin existencias, debe comprobarse y descontarse de forma coordinada, con una regla de concurrencia explícita.

### Consulta de pedidos

`GET /orders` debe filtrar por el usuario autenticado y devolver una página de resultados con orden estable. Si se vuelve lento, revisar las consultas ejecutadas, la carga de líneas y un índice acorde al filtro y orden, por ejemplo sobre `user_id`, fecha e ID. La necesidad concreta del índice debe confirmarse con el plan de consulta.

## Estructura preferida para FastAPI

La estructura propuesta por el usuario es:

```text
app/
├── controllers/
├── routes/
├── utils/
├── models/
├── database/
└── services/
docs/
tests/
scripts/
```

Se sugirió añadir `schemas/` para los modelos de entrada y salida, además de configuración y dependencias compartidas cuando hagan falta. La división de responsabilidades acordada es:

- **Route:** declara URL, método HTTP y dependencias.
- **Controller:** recibe y coordina la petición; construye la respuesta HTTP.
- **Service:** ejecuta reglas de negocio, como calcular el total y crear una orden.
- **Database:** configura conexión y sesiones.
- **Model:** representa tablas y relaciones.
- **Schema:** define y valida entrada y salida de la API.
- **Utils:** funciones compartidas con una responsabilidad concreta.

Para crear una orden, conviene que una operación de servicio coordine **una sola transacción**. Si varios servicios pequeños confirman sus cambios por separado, puede quedar una orden guardada a medias. `routes` y `controllers` pueden coexistir siempre que cada capa aporte una responsabilidad clara.

## Evaluación y próximos pasos

**Fortalezas observadas:** criterio de negocio, diseño de relaciones y capacidad para detectar problemas una vez planteado un caso concreto. El usuario ya aplica JWT, roles, API keys y restricciones de acceso a datos propios en sus sistemas.

**Conceptos que conviene practicar al explicarlos en voz alta:** precio histórico en líneas de pedido, transacciones, concurrencia y actualización perdida, autorización por recurso, y consulta real que ejecuta cada endpoint.

**Siguiente práctica recomendada:** resolver un ejercicio pequeño de FastAPI con base de datos y explicar cada endpoint de principio a fin: contrato HTTP, validación, autorización, reglas, consulta, transacción, errores y pruebas. La IA puede ayudar a escribirlo, pero cada decisión debe poder defenderse.
