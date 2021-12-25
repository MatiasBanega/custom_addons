# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    "name": "Migrate Product From version 10 to 14",
    "version": "14.0.1.0",
    "category": "sale",
    "summary": "Allow to sync product between two odoo database",
    "description": """
    Sync all products between two database of odoo.
    """,
    "author": "Warlock Technologies Pvt Ltd.",
    "website": "http://warlocktechnologies.com",
    "support": "info@warlocktechnologies.com",
    "depends": ["website", "mail", "stock", "sale", "website_sale", "purchase"],
    "data": [
        "data/ir_cron.xml",
        "security/ir.model.access.csv",
        "wizard/message_view.xml",
        "views/product_sync_view.xml",
        "views/product_template_view.xml",
        "views/ir_cron_view.xml",
    ],
    "images": ["images/screen_image.png"],
    "price": 50,
    "currency": "USD",
    "license": "OPL-1",
    "installable": True,
}
