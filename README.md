# Ejercicio: construye tú la API

Esta carpeta comenzó con la infraestructura y los datos. PostgreSQL ya
tiene tablas y registros; Redis queda listo para la cola. La API de productos
está en desarrollo y ya están implementados `POST /auth/login` y `GET /auth/me`.
El contexto del caso está en `resumen.md`. La descripción completa de tablas,
columnas, tipos y relaciones está en `db/SCHEMA.md`.

## Levantar la base de datos

```bash
docker compose up -d
docker compose ps
docker compose exec db psql -U practice -d practice
```

La primera vez, PostgreSQL ejecuta `db/init/01_schema.sql` y
`db/init/02_seed.sql`. El volumen conserva los datos entre reinicios.
**Solo si quieres borrar todo y volver al seed:**

```bash
docker compose down -v
docker compose up -d
```

La contraseña de PostgreSQL está en el `.env` local (no se sube a Git).
Ese archivo también contiene `JWT_SECRET_KEY`, la clave para firmar tokens.

| Servicio | Desde tu computadora | Desde otro servicio del mismo Compose |
| --- | --- | --- |
| PostgreSQL | `localhost:5433`, base `practice`, usuario `practice` | `db:5432` |
| Redis | `redis://localhost:6380/0` | `redis://redis:6379/0` |

Puedes comprobar el seed sin modificar datos:

```bash
docker compose exec -T db psql -U practice -d practice -f /dev/stdin < db/verify.sql
docker compose exec db psql -U practice -d practice -c 'SELECT username, role FROM users;'
docker compose exec db psql -U practice -d practice -c 'SELECT name, price_cents, stock FROM products;'
```

La primera consulta debe devolver **cero filas**. El seed tiene 3 usuarios,
6 productos, 4 pedidos, 6 líneas, 12 movimientos y 1 trabajo de comprobante.
Los usuarios `ana`, `luis` y `admin` usan la contraseña de prueba
`Demo12345!`, guardada como hash bcrypt. Los precios están en centavos.

## Probar la autenticación

`POST /auth/login` recibe `username` y `password` como datos de formulario y
devuelve `access_token` y `token_type`. El token dura 30 minutos. En `/docs`
puedes iniciar sesión desde el botón **Authorize**; también puedes enviarlo
en el encabezado `Authorization: Bearer <token>` a `GET /auth/me`.
Los roles guardados en `users.role` son `customer` y `admin`. Crear un producto
con `POST /products/` requiere un token de `admin`: sin token devuelve 401 y
con token de `customer` devuelve 403.

## Contrato que debes implementar

| Método | Ruta | Comportamiento esperado |
| --- | --- | --- |
| `POST` | `/auth/login` | Recibe `username` y `password`; devuelve JWT válido o 401. |
| `GET` | `/products` | Lista productos activos con ID, nombre, precio y stock. |
| `PATCH` | `/products/{id}` | Solo `admin` puede cambiar `price_cents` o `active`; valida los datos y devuelve el producto. |
| `GET` | `/orders?limit=20&offset=0` | Lista solo pedidos del usuario autenticado, con orden estable y paginación. |
| `GET` | `/orders/{id}` | Devuelve un pedido y sus líneas solo si pertenece al usuario; de lo contrario, 404. |
| `POST` | `/orders` | Crea un pedido a partir de una lista de `{product_id, quantity}`; devuelve el pedido creado (201). |
| `POST` | `/orders/{id}/receipt-jobs` | Registra y encola la generación de un comprobante; devuelve el ID del trabajo (202). |
| `GET` | `/receipt-jobs/{id}` | Devuelve estado y resultado del trabajo solo a su dueño; de lo contrario, 404. |

### Reglas del pedido

- La lista de productos no puede estar vacía; cada cantidad debe ser positiva;
  no aceptes el mismo producto dos veces en un pedido.
- Rechaza productos inexistentes o inactivos. No aceptes precios ni totales
  enviados por el cliente: usa el precio actual de `products`.
- Guarda ese precio en `order_items.unit_price_cents` para conservar el precio
  histórico. `orders.total_cents` debe ser la suma de las líneas.
- El `PATCH` de producto no debe modificar `stock`; el saldo se cambia con
  movimientos de inventario, no con una edición libre del catálogo.
- Crea encabezado, líneas, movimientos de inventario y descuentos de stock en
  **una sola transacción**. Si falla cualquier paso, no debe quedar nada a medias.
- El inventario **puede ser negativo**. Dos compras simultáneas deben descontar
  ambas cantidades; evita la actualización perdida.

### Autenticación y cola

- Comprueba el hash bcrypt del usuario y valida firma, algoritmo y expiración
  del JWT. No pongas el secreto JWT en el código fuente.
- Usa el usuario autenticado para filtrar pedidos y trabajos en la consulta
  a PostgreSQL. Un ID UUID no sustituye la autorización.
- Usa Redis como broker de una tarea ejecutada por un worker separado de
  FastAPI (por ejemplo, Celery). El worker genera un comprobante a partir de
  `orders` y `order_items`, y actualiza `receipt_jobs.status` y `.result`.
- El trabajo debe ser seguro de reintentar: repetirlo no crea otro pedido ni
  vuelve a descontar inventario. Si no se puede publicar en Redis, devuelve
  un error controlado y evita dejar un trabajo engañosamente en `queued`.

### Errores y pruebas esperadas

Devuelve errores HTTP claros para credenciales inválidas, token ausente o
inválido, datos inválidos, producto inexistente, recurso ajeno y cola caída.
Prueba al menos:

1. `ana` ve sus dos pedidos y no los dos de `luis`.
2. El primer pedido de `ana` conserva Café a 1300 centavos aunque el catálogo
   muestra 1500; el total es 6100.
3. Un pedido con una línea inválida no cambia pedidos, movimientos ni stock.
4. Dos ventas del mismo producto descuentan ambas cantidades, incluso si
   dejan stock negativo.
5. Un usuario no puede consultar el trabajo de comprobante de otro.
6. El worker procesa una tarea real publicada en Redis.
7. `ana` no puede editar productos y `admin` sí; cambiar un precio actual no
   altera los precios guardados en pedidos previos.

## Cómo evaluaré tu solución

Cuando termines, revisaré el contrato HTTP y la validación; autenticación y
acceso por usuario; transacción, precio histórico y concurrencia; integración
real de Redis y worker; y pruebas que demuestren estos comportamientos. Te
daré fallos concretos, su gravedad y cómo reproducirlos.
