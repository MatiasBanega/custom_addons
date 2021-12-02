# -*- coding: utf-8 -*-
# Copyright (c) 2019-Present Droggol. (<https://www.droggol.com/>)

{
    'name': 'Droggol Theme Common',
    'description': 'Droggol Theme Common',
    'category': 'eCommerce',
    'version': '14.0.0.2.2',
    'depends': [
        'sale_product_configurator',
        'website_sale_comparison',
        'website_sale_wishlist',
        'website_sale_stock',
    ],

    'license': 'OPL-1',
    'author': 'Droggol',
    'company': 'Droggol',
    'maintainer': 'Droggol',
    'website': 'https://www.droggol.com/',

    'price': 15.00,
    'currency': 'USD',
    'live_test_url': '',

    'data': [
        'security/ir.model.access.csv',
        'data/groups.xml',
        'views/assets.xml',
        'views/backend_templates.xml',
        'views/dr_config_template.xml',

        # Backend
        'views/backend/menu_label.xml',
        'views/backend/website_menu.xml',
        'views/backend/product_brand.xml',
        'views/backend/product_label.xml',
        'views/backend/product_tags.xml',
        'views/backend/product_template.xml',
        'views/backend/product_attribute.xml',
        'views/backend/product_pricelist.xml',
        'views/backend/pwa_shortcuts.xml',
        'views/backend/res_config_settings.xml',
        'views/backend/dr_config.xml',
        'views/backend/category_label.xml',
        'views/backend/product_category.xml',
    ],
    'qweb': [
        'static/src/xml/backend/list_view_brand.xml',
    ],
}
