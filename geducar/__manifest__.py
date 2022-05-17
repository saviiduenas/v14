# -*- coding: utf-8 -*-


{
    'name': 'Geducar',
    'version': '1.0',
    'category': 'Hidden',
    'sequence': 6,
    'summary': 'Modulo Geducar',
    'description': """

""",
    'depends': ['sale','account'],
    'data': [
        'views/report.xml',
        'views/reporte_pago.xml',
        'views/account_move_views.xml',
        'views/sale_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
