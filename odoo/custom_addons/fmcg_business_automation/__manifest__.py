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
        'data/stock_picking_activity_types.xml',
        'data/automation_picking_draft.xml',
        'data/action_create_incoming_lot_serial.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
