{
    "name": "FMCG Stock Picking Dashboard",
    "version": "19.0.1.0.0",
    "category": "Inventory/Inventory",
    "summary": "Operational dashboard for transfers waiting at each processing stage",
    "depends": ["stock"],
    "data": [
        'views/stock_picking_bulk_activity_action.xml',
        "views/stock_picking_dashboard_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "fmcg_stock_picking_dashboard/static/src/views/stock_picking_dashboard.js",
            "fmcg_stock_picking_dashboard/static/src/views/stock_picking_dashboard.xml",
            "fmcg_stock_picking_dashboard/static/src/views/stock_picking_dashboard.scss",
        ],
    },
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
