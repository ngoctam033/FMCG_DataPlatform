{
    'name': 'FMCG Inventory Learning - Data',
    'version': '1.0',
    'category': 'Inventory/Inventory',
    'summary': 'Master data for FMCG inventory simulation',
    'depends': ['stock', 'product_expiry', 'sale_management', 'purchase', 'uom'],
    'data': [
        'data/res_partner_data.xml',
        'data/uom_data.xml',
        'data/product_category_data.xml',
        'data/product_data.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
