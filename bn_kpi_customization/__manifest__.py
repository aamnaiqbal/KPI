{
    'name': 'KPI Customization',
    'version': '1.0',
    'summary': 'kpi customaization',
    'author': 'BytesNode',
    'website': 'http://bytesnode.com',
    'license': 'LGPL-3',
    'category': 'BytesNode',
    'depends': ['base', 'crm'],
    'data': [
        'security/ir.model.access.csv',
        'views/kpi_view.xml',
        'views/parameter_master_setup.xml',
        'views/crm_team_view.xml',
    ],
    'assets': {
    },

    'auto_install': False,
    'application': True,
}