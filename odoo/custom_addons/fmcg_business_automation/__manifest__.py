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
        'data/stock_move_validate_positive_demand.xml',
        'data/ir_filter_stock_picking_missing_lot_serial.xml',
        'data/mail_activity_unique_active_type.xml',
        'data/stock_picking_generate_missing_moves.xml',
        'data/stock_picking_draft_confirmation.xml',
        'data/mail_activity_type_validate_assigned_picking.xml',
        'data/stock_picking_schedule_draft_confirmation.xml',
        'data/stock_picking_schedule_validate_on_assigned.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
