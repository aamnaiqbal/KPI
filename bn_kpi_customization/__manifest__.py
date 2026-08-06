{
    'name': 'KPI Customization',
    'version': '1.0',
    'summary': 'kpi customaization',
    'author': 'BytesNode',
    'website': 'http://bytesnode.com',
    'license': 'LGPL-3',
    'category': 'BytesNode',
    'depends': ['base', 'crm', 'sale_management', 'contacts', 'account', 'hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'views/kpi_view.xml',
        'views/parameter_master_setup.xml'
    ],
    'assets': {
    },

    'auto_install': False,
    'application': True,
}