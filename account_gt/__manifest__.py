# -*- coding: utf-8 -*-
{
    'name': "account_gt",

    'summary': """ Conta extra para guate """,

    'description': """
        Conta extra para guate
    """,

    'author': "JS",
    'website': "",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['account','base'],

    'data': [
        'views/report.xml',
        'views/res_partner_views.xml',
        'views/account_gt_views.xml',
        'views/account_move_views.xml',
        'views/account_payment_view.xml',
        'report/reporte_libro_compras_views.xml',
        'report/reporte_libro_ventas_views.xml',
        'report/reporte_libro_bancos_views.xml',
        'report/reporte_libro_conciliacion_bancaria_views.xml',
        'wizard/libro_compras_wizard_views.xml',
        'wizard/libro_ventas_wizard_views.xml',
        'wizard/libro_bancos_wizard_views.xml',
        'wizard/libro_conciliacion_bancaria_wizard_views.xml',
        'wizard/conciliacion_bancaria_wizard_views.xml',
        'data/ir_sequence_data.xml',
    ],
}
