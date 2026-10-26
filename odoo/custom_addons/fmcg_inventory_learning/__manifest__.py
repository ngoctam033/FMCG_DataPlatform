{
    'name': 'FMCG Inventory Learning - Data',
    'version': '1.0',
    'category': 'Inventory/Inventory',
    'summary': 'Master data for FMCG inventory simulation',
    'depends': ['stock', 'product_expiry', 'sale_management', 'purchase', 'uom'],
    'data': [
        'data/res_partner_data.xml',
        'data/fmcg_partners_data.xml',
        'data/res_groups_data.xml',
        'data/res_users.xml',
        'data/res_users_inventory_groups.xml',
        
        'data/fmcg_pricing_data.xml',

        'data/inventory_master_data.xml',
        'data/fmcg_catalog_data.xml',
        'data/fmcg_supplierinfo_data.xml',
        
        'data/stock_data.xml',
        'data/fmcg_advanced_stock_routes.xml',
        'data/fmcg_inventory_data.xml',
        'data/fmcg_warehouse_scenarios.xml',
        # 'data/fmcg_mrp_data.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
