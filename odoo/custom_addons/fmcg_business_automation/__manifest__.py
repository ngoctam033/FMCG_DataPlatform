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
        'data/stock_picking_activity_duplicate_guard.xml',
        'data/stock_picking_state_activity_types.xml',
        'data/stock_picking_assign_activity.xml',
        'data/stock_picking_assigned_activity_automation.xml',
        'data/stock_picking_initial_state_automation.xml',
        'data/stock_picking_confirm_automation.xml',
        'data/stock_picking_assigned_automation.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
