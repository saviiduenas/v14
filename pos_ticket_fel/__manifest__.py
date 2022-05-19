# -*- coding: utf-8 -*-


{
    'name': 'POS TICKET FEL',
    'version': '1.0',
    'category': 'Hidden',
    'sequence': 6,
    'summary': 'TIKCET POS FEL',
    'description': """

""",
    'depends': ['point_of_sale'],
    'data': [
        'views/templates.xml',
        'views/pos_order_view.xml',
    ],
    'qweb': [
        'static/src/xml/Screens/ReceiptScreen/OrderReceipt.xml',
    ],
    'installable': True,
    'auto_install': False,
}
