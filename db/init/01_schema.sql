CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE users (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    username varchar(80) NOT NULL UNIQUE,
    password_hash text NOT NULL,
    role varchar(20) NOT NULL DEFAULT 'customer'
        CHECK (role IN ('customer', 'admin')),
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE products (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name varchar(120) NOT NULL UNIQUE,
    price_cents integer NOT NULL CHECK (price_cents >= 0),
    stock integer NOT NULL DEFAULT 0,
    active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE orders (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES users(id),
    status varchar(20) NOT NULL DEFAULT 'confirmed'
        CHECK (status IN ('confirmed', 'cancelled')),
    total_cents integer NOT NULL CHECK (total_cents >= 0),
    created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX orders_user_created_id_idx
    ON orders (user_id, created_at DESC, id DESC);

CREATE TABLE order_items (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id uuid NOT NULL REFERENCES orders(id),
    product_id uuid NOT NULL REFERENCES products(id),
    quantity integer NOT NULL CHECK (quantity > 0),
    unit_price_cents integer NOT NULL CHECK (unit_price_cents >= 0),
    UNIQUE (order_id, product_id)
);
CREATE INDEX order_items_order_id_idx ON order_items (order_id);

-- products.stock es el saldo actual; los movimientos dejan una auditoría.
-- El saldo puede ser negativo, según la regla del ejercicio.
CREATE TABLE inventory_movements (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id uuid NOT NULL REFERENCES products(id),
    order_id uuid REFERENCES orders(id),
    delta integer NOT NULL CHECK (delta <> 0),
    reason varchar(20) NOT NULL CHECK (reason IN ('opening', 'sale')),
    created_at timestamptz NOT NULL DEFAULT now(),
    CHECK (
        (reason = 'opening' AND order_id IS NULL AND delta > 0)
        OR (reason = 'sale' AND order_id IS NOT NULL AND delta < 0)
    )
);
CREATE INDEX inventory_movements_product_created_idx
    ON inventory_movements (product_id, created_at DESC);

CREATE TABLE receipt_jobs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id uuid NOT NULL REFERENCES orders(id),
    user_id uuid NOT NULL REFERENCES users(id),
    status varchar(20) NOT NULL DEFAULT 'queued'
        CHECK (status IN ('queued', 'running', 'completed', 'failed')),
    result jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX receipt_jobs_user_created_idx
    ON receipt_jobs (user_id, created_at DESC);
