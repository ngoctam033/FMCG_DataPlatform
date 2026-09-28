# Power BI — Odoo PostgreSQL connection

`R1` contains an import-mode diagnostic table named `Odoo Database Objects`.
It connects to the PostgreSQL database used by the local Odoo simulator and
lists the Odoo tables visible in the `public` schema.

## Connection parameters

| Parameter | Default | Purpose |
|---|---|---|
| `OdooServer` | `192.168.139.1` | Linux host on the VMware NAT network (`vmnet8`) |
| `OdooPort` | `5433` | Host port published by the Odoo Compose stack |
| `OdooDatabase` | `fmcg_erp` | Odoo database name |

The current Windows VM is `192.168.139.128`; the database does not run at that
address. Power BI must connect to the Linux host at `192.168.139.1`. Keep port
`5433` unless the Compose port mapping is changed.

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

## Warehouse alert thresholds

The report exposes alert KPIs and row-level status labels on **Tổng quan kho**,
**Tồn kho & bổ sung**, and **Lô & hạn sử dụng**.

| Level | Inventory rule | Expiry rule |
|---|---|---|
| 🔴 Critical | Available quantity `<= 0`, available quantity `> 120%` of Max, or reserved quantity exceeds on-hand quantity | Already expired |
| 🟠 Warning | Available quantity is below Min, or is above Max up to `120%` of Max | Expires in `0–30` days |
| 🔵 Watch | Available quantity is between Min and `120%` of Min | Expires in `31–60` days |
| 🟢 Normal | None of the alert rules above | More than `60` days remaining or no actionable expiry alert |

The `20%` buffer is currently defined in the DAX measures and calculated
columns in `FactBoSungHang.tmdl`. Change the measures and the row-level status
columns together if the business threshold is revised.
