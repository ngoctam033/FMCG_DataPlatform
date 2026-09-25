{
    'name': 'Employee Action Simulator',
    'version': '1.0',
    'summary': 'Giả lập các hành vi thao tác của nhân viên trên hệ thống',
    'category': 'Tools',
    'author': 'Antigravity',
    'depends': ['base', 'stock', 'base_automation'], # Phụ thuộc module stock để gọi stock.picking
    'data': [
        'data/cron_data.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
