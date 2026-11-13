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
        'data/mail_activity_unique_active_type.xml',
        'data/stock_picking_draft_confirmation.xml',
        'data/stock_picking_schedule_draft_confirmation.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
