# -*- coding: utf-8 -*-
# Copyright (c) 2019-Present Droggol. (<https://www.droggol.com/>)

from odoo import api, fields, models


class DrWebsiteMenuLabel(models.Model):
    _name = 'dr.website.menu.label'
    _description = 'Website Menu Label'

    name = fields.Char(required=True, translate=True)
    color = fields.Selection([
        ('green', 'Green'),
        ('blue', 'Blue'),
        ('red', 'Red'),
        ('orange', 'Orange'),
        ('gray', 'Gray'),
        ('black', 'Black'),
    ])
    menu_ids = fields.One2many('website.menu', 'dr_menu_label_id')
    menu_count = fields.Integer(compute='_compute_menu_count')

    def _compute_menu_count(self):
        for label in self:
            label.menu_count = len(label.menu_ids)

    def action_open_menus(self):
        self.ensure_one()
        action = self.env.ref('website.action_website_menu').read()[0]
        action['domain'] = [('dr_menu_label_id', '=', self.id)]
        action['context'] = {}
        return action


class WebsiteMenu(models.Model):
    _inherit = 'website.menu'

    dr_menu_label_id = fields.Many2one('dr.website.menu.label', string='Label')
    dr_is_special_menu = fields.Boolean()

    @api.model
    def get_tree(self, website_id, menu_id=None):
        result = super(WebsiteMenu, self).get_tree(website_id, menu_id)
        for menu in result['children']:
            menu['fields']['dr_is_special_menu'] = self.browse(menu['fields']['id']).dr_is_special_menu
        return result
