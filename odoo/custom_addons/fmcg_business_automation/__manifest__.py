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
        'data/automation_picking_assigned.xml',
        'data/automation_picking_backorder.xml',
        'data/stock_picking_missing_moves_workflow.xml',
        'data/action_create_incoming_lot_serial.xml',
        'data/stock_picking_missing_lot_serial_workflow.xml',
        'data/stock_picking_existing_lot_workflow.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
