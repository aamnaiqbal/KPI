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
        'views/parameter_master_setup.xml',
        'views/dashboard_action.xml'
    ],
    'assets': {

        'web.assets_backend': [

            'bn_kpi_customization/static/src/dashboard/dashboard.js',

            'bn_kpi_customization/static/src/dashboard/dashboard.xml',

            'bn_kpi_customization/static/src/dashboard/dashboard.scss',

        ],

    },
    'auto_install': False,
    'application': True,
}