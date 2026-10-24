# Power BI — Odoo PostgreSQL connection

`R1` contains an import-mode diagnostic table named `Odoo Database Objects`.
It connects to the PostgreSQL database used by the local Odoo simulator and
lists the Odoo tables visible in the `public` schema.

## Connection parameters

| Parameter | Default | Purpose |
|---|---|---|
| `OdooServer` | `192.168.139.1` | Linux host on the VMware NAT network (`vmnet8`) |
| `OdooPort` | `5432` | Host port published by the Odoo Compose stack |
| `OdooDatabase` | `fmcg_core` | Odoo database name |

The current Windows VM is `192.168.139.128`; the database does not run at that
address. Power BI must connect to the Linux host at `192.168.139.1`. Keep port
`5432` unless the Compose port mapping is changed.

## First refresh

1. Start the Odoo PostgreSQL stack.
2. Open `R1.pbip` in Power BI Desktop.
3. Open **Transform data > Edit parameters** and confirm that `OdooServer` is
   `192.168.139.1`.
4. Refresh the model.
5. When prompted, choose **Database** authentication and enter a PostgreSQL
   account that has read-only access to the Odoo database.

Credentials are intentionally not stored in the PBIP project. A successful
refresh returns one row per visible Odoo table. This diagnostic table can be
removed after the business tables and analytics model are defined.

## Query architecture

Every PostgreSQL native query is intentionally limited to `SELECT * FROM
<base_table>`. Joins, filters, null handling, calendar generation, and other
shaping steps are implemented in Power Query. Relationships between the shaped
fact and dimension tables are defined in the semantic model.

Replenishment uses Odoo's stored `qty_to_order_computed` and
`qty_to_order_manual` fields from `stock_warehouse_orderpoint`; the report does
not reimplement Odoo's replenishment algorithm from `stock_quant`.

## Warehouse alert thresholds

The report exposes alert KPIs and row-level status labels on **Tổng quan kho**,
**Tồn kho & bổ sung**, and **Lô & hạn sử dụng**.

| Level | Inventory rule | Expiry rule |
|---|---|---|
| 🔴 Critical | Reserved quantity exceeds on-hand quantity | Already expired |
| 🟠 Warning | Odoo reports a positive replenishment quantity | Expires in `0–30` days |
| 🔵 Watch | Not inferred from orderpoint data | Expires in `31–60` days |
| 🟢 Normal | Odoo reports no replenishment quantity | More than `60` days remaining or no actionable expiry alert |

Power BI does not infer out-of-stock, near-Min, or over-Max states from
`stock_warehouse_orderpoint`, because the ORM-computed `qty_on_hand` and
`qty_forecast` fields are not stored in PostgreSQL. Those states require an
Odoo API/reporting source that exposes the computed fields.
