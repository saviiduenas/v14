# -*- coding: utf-8 -*-


{
    'name': 'DIGIFACT FEL',
    'version': '1.0',
    'category': 'Hidden',
    'sequence': 6,
    'summary': 'Módulo para facturacion en linea DIGIFACT',
    'description': """

""",
    'depends': ['account'],
    'data': [
        'views/account_view.xml',
        'views/res_company_views.xml',
        'views/account_invoice_view.xml',
        'views/res_partner_view.xml',
        'views/report_invoice.xml',
        'views/reporte_ticket.xml',
        'data/paperformat_ticket.xml',
        'views/report.xml',
    ],
    'installable': True,
    'auto_install': False,
}
