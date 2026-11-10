{
    'name': 'FMCG Business Automation',
    'version': '19.0.1.0.0',
    'summary': 'Custom business automations for the FMCG platform',
    'category': 'Tools',
    'author': 'FMCG Data Platform',
    'depends': [
        'stock',
        'base_automation',
    ],
    'data': [
        'data/mail_activity_type_backorder_request.xml',
        'data/stock_picking_validate_activity_data.xml',
        'data/stock_picking_confirm_activity_data.xml',
        'data/stock_transfer_trouble.xml',
        'data/stock_move_quantity_validation.xml',
        'data/mail_activity_missing_lot_serial.xml',
        'data/stock_picking_missing_lot_automation.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
