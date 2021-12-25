
# -*- coding: utf-8 -*-
{
    'name': "Import product",
    'category': "Technical",
    'summary': "",
    'description': """
    """,
    "author": "Techones",
    'depends': [
        'product',
        'base',
        'stock'
    ],
    'data': [
        'security/ir.model.access.csv',
        'import_product_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}