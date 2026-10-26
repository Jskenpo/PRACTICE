-- Debe devolver cero filas: cualquier fila indica una inconsistencia.
SELECT 'order_total' AS problem, o.id::text AS id
FROM orders o
JOIN (SELECT order_id, SUM(quantity * unit_price_cents) AS calculated
      FROM order_items GROUP BY order_id) x ON x.order_id = o.id
WHERE o.total_cents <> x.calculated
UNION ALL
SELECT 'stock', p.id::text
FROM products p
JOIN (SELECT product_id, SUM(delta) AS calculated
      FROM inventory_movements GROUP BY product_id) x ON x.product_id = p.id
WHERE p.stock <> x.calculated;
