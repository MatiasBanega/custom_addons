# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
    "name":  "Odoo Multichannel Woocommerce connector",
    "summary":  """Woocommerce Odoo Connector integrates Odoo with Woocommerce. Manage your Woocommerce store in Odoo. Handle Woocommerce orders in Odoo. Ecommerce Connector""",
    "category":  "Website",
    "version":  "1.0.8",
    "sequence":  1,
    "author":  "Webkul Software Pvt. Ltd.",
    "license":  "Other proprietary",
    "website":  "https://store.webkul.com/Woocommerce-Odoo-Connector.html",
    "description":  """Woocommerce Odoo Connector
                                          Odoo Woocommerce connector
                                          Odoo Woocommerce bridge
                                          Woocommerce bridge
                                          Odoo Woocommerce
                                          Connect Woocommerce with Odoo
                                          Manage Woocommerce in Odoo
                                          Woocommerce Odoo data transfer
                                          Woocommerce store in Odoo
                                          Integrate Odoo with Woocommerce
                                          Integrate Woocommerce with Odoo
                                          Woocommerce order in Odoo
                                          Ecommerce website to Odoo
                                          E-commerce website to Odoo
                                          Connect ecommerce website
                                          E-commerce Connector
                                          Ecommerce Connector""",
    "live_test_url":  "http://wpodoo.webkul.com/woocommerce_odoo_connector/",
    "depends":  ['odoo_multi_channel_sale'],
    "qweb":  ["views/inherit_multi_channel_template.xml", ],
    "data":  [
        'data/demo.xml',
        'views/woc_config_views.xml',
        'views/inherited_woocommerce_dashboard_view.xml',
        'wizard/import_operation.xml',
        'wizard/export_product_view.xml',
        'wizard/export_template_view.xml',
        'wizard/export_category_view.xml',
    ],
    "images":  ['static/description/banner.gif'],
    "application":  True,
    "installable":  True,
    "auto_install": False,
    "price":  100,
    "currency":  "USD",
    "external_dependencies":  {'python': ['woocommerce']},
}
