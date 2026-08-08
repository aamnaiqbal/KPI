{
    'name': 'KPI Customization',
    'version': '1.0',
    'summary': 'kpi customaization',
    'author': 'BytesNode',
    'website': 'http://bytesnode.com',
    'license': 'LGPL-3',
    'category': 'BytesNode',
    'depends': ['base', 'crm', 'sale_management', 'contacts', 'account', 'hr_attendance', 'eh_board'],
    'data': [
        'security/ir.model.access.csv',
        'views/kpi_view.xml',
        'views/dashboard_menu.xml',
        'views/parameter_master_setup.xml',
        'views/employee_target.xml',
    ],
    'auto_install': False,
    'application': True,
}