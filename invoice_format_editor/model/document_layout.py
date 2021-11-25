# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AddDocumentTemplate(models.Model):
    _name = "doc.layout"
    _description = 'Adding the fields for customization'
    _rec_name = 'name'

    name = fields.Char("Name")

    base_color = fields.Char("Base Color",
                             help="Background color for the invoice")

    heading_text_color = fields.Char("Heading text Color",
                                     help="Heading Text color")

    text_color = fields.Char("Text Color", help="Text color of items")

    customer_text_color = fields.Char("Customer Text Color",
                                      help="Customer address text color")

    company_text_color = fields.Char("Company Text Color",
                                     help="Company address Text color")

    logo_position = fields.Selection([('left', 'Left'), ('right', 'Right')],
                                     string="Logo Position",
                                     help="Company logo position")

    customer_position = fields.Selection(
        [('left', 'Left'), ('right', 'Right')], string="Customer position",
        help="Customer address position")

    company_position = fields.Selection([('left', 'Left'), ('right', 'Right')],
                                        string="Company Address Position",
                                        help="Company address position")

    sales_person = fields.Boolean('Sales person', default=False,
                                  help="Sales Person")
    description = fields.Boolean('Description', default=False,
                                 help="Description")
    hsn_code = fields.Boolean('HSN Code', default=False, help="HSN code")
    tax_value = fields.Boolean('Tax', default=False, help="Tax")
    reference = fields.Boolean('Reference', default=False,
                               help="Customer Reference")
    source = fields.Boolean('Source', default=False,
                            help="Source Document")
    address = fields.Boolean('Address', default=False,
                             help="Address")
    city = fields.Boolean('City', default=False,
                          help="City")
    country = fields.Boolean('Country', default=False,
                             help="Country")
