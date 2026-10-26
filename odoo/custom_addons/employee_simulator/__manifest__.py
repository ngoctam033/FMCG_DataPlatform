{
    'name': 'Employee Action Simulator',
    'version': '1.0',
    'summary': 'Giả lập các hành vi thao tác của nhân viên trên hệ thống',
    'category': 'Tools',
    'author': 'Antigravity',
    'depends': [
        'base',
        'mail',
        'stock',
        'base_automation',
        'fmcg_inventory_learning',
    ],
    'data': [
        'data/cron_data.xml',
        'data/cron_internal_transfer.xml',
        'data/activity_data.xml',
        'views/mail_activity_sla_dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'employee_simulator/static/src/views/mail_activity_sla_dashboard.js',
            'employee_simulator/static/src/views/mail_activity_sla_dashboard.xml',
            'employee_simulator/static/src/views/mail_activity_sla_dashboard.scss',
        ],
    },
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
