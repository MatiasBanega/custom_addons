# -*- coding: utf-8 -*-

# Copyright © 2021 Garazd Creation (<https://garazd.biz>)
# @author: Yurii Razumovskyi (<support@garazd.biz>)
# @author: Iryna Razumovska (<support@garazd.biz>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

{
    'name': 'Google Analytics 4 Global Site Tag (gtag.js)',
    'version': '14.0.1.0.1',
    'category': 'Website',
    'author': 'Garazd Creation',
    'website': 'https://garazd.biz',
    'license': 'LGPL-3',
    'summary': 'Google Analytics 4 Global Site Tag (gtag.js)',
    'images': ['static/description/banner.png'],
    'live_test_url': 'https://apps.garazd.biz/r/DNy',
    'description': """
Activate the Google Analytics 4 Global Site Tag on a website. Add the GA4 events Login and Sign Up.
    """,
    'depends': [
        'website',
    ],
    'data': [
        'views/res_config_settings_views.xml',
        'views/website_templates.xml',
    ],
    'external_dependencies': {
    },
    'support': 'support@garazd.biz',
    'application': False,
    'installable': True,
    'auto_install': False,
}

