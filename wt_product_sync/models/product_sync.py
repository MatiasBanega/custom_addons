# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from html.parser import HTMLParser
from xmlrpc import client as xmlrpclib
import xmlrpc.client
import datetime
from odoo.exceptions import ValidationError


class HTMLFilter(HTMLParser):
    text = ""

    def handle_data(self, data):
        self.text += data


class ProductSync(models.Model):
    _name = "product.sync"
    _description = "Product Store"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Store Name", required=True, tracking=1, help="Store Name you would like to have")
    url = fields.Char(string="Url", tracking=1, help="url of database you want to fetch data http://warlocktechnologies.com", required=True,)
    database = fields.Char(string="Database", tracking=1, help="database name of the target url", required=True,)
    username = fields.Char(string="User Name", tracking=1, help="admin user name of target url", required=True,)
    password = fields.Char(string="Password", tracking=0, help="password of user name of target url", required=True,)
    active = fields.Boolean(default=True)
    interval_number = fields.Integer(default=1, help="Repeat every x.")
    interval_type = fields.Selection([("minutes", "Minutes"), ("hours", "Hours"), ("days", "Days"), ("weeks", "Weeks"), ("months", "Months"),], string="Interval Unit", default="months",)
    cron_id = fields.Many2one("ir.cron", "Cron Id", readonly=True)
    product_ids_history = fields.Text(string="Product ID History")
    sync_tracker = fields.Integer(string="String Tracker")

    # @api.model
    # def create(self, vals):
    #     res = super(ProductSync, self).create(vals)
    #     if res:
    #         ir_model = self.env["ir.model"].sudo().search([("model", "=", res._name)])
    #         date = datetime.datetime.now() + datetime.timedelta(minutes=2)
    #         cron = self.env["ir.cron"].create(
    #             {
    #                 "name": "[" + res.name + "]" + " : Sync Product data",
    #                 "model_id": ir_model.id,
    #                 "state": "multi",
    #                 "interval_number": res.interval_number,
    #                 "interval_type": res.interval_type,
    #                 "active": True,
    #                 "numbercall": -1,
    #                 "store_id": res.id,
    #                 "nextcall": date,
    #             }
    #         )
    #         res.cron_id = cron.id
    #     return res

    # def write(self, vals):
    #     res_update = super(ProductSync, self).write(vals)
    #     if vals.get("name"):
    #         self.cron_id.name = "[" + vals.get("name") + "]" + " : Sync Product data"
    #     if vals.get("interval_number"):
    #         self.cron_id.interval_number = vals.get("interval_number")
    #     if vals.get("interval_type"):
    #         self.cron_id.interval_type = vals.get("interval_type")
    #     return res_update

    def unlink(self):
        for rec in self:
            if rec.cron_id:
                rec.sudo().cron_id.unlink()
        return super(ProductSync, self).unlink()

    def convert_html_to_text(self, data):
        converted_text = ""
        if data:
            f = HTMLFilter()
            f.feed(data)
            converted_text += f.text or ""
        return converted_text

    # Product Category
    def get_product_category(self, category):
        category = category[1].split("/")
        categ_id = False
        parent_id = [0]
        product_category_obj = self.env["product.category"]
        for catg_len in range(len(category)):
            categ_id = product_category_obj.search(
                [("name", "=", category[catg_len].strip())], limit=1
            )
            if not categ_id:
                categ_id = product_category_obj.create(
                    {"name": category[catg_len].strip()}
                )
            is_categ = product_category_obj.search(
                [("id", "=", parent_id[0])], limit=1
            )
            if is_categ:
                categ_id.parent_id = is_categ.id
            parent_id[0] = categ_id.id
        return categ_id

    # Website Categories
    def sync_web_category(self):
        public_categ_ids = self.established_connection('product.public.category', 'search_read', [], False)
        Category = self.env['product.public.category']                     
        for rec_id in public_categ_ids:
            category_id = Category.search([('store_id', '=', rec_id['id'])])

            parent_id = False
            if rec_id.get('parent_id'):
                parent_id = Category.search([('store_id', '=', rec_id['parent_id'])])

            category_vals = {
                'name': rec_id.get('name'),
                'store_id': rec_id.get('id'),
                'parent_id': parent_id.id if parent_id else False,
            }
            if not category_id:
                Category.create(category_vals)
            else:
                category_id.write(category_vals)

    # Website product images
    def sync_web_product_images(self, product):
        ProductImage = self.env['product.image']
        images = self.established_connection('product.image', 'search_read', [['product_tmpl_id', '=', product['id']]], False)
        for rec_id in images:
            image_id = ProductImage.search([('store_id', '=', rec_id['id'])])
            image_vals = {
                "store_id": rec_id['id'],
                "name": rec_id.get("name"),
                "image_1920": rec_id.get("image_1920"),
            }
            if not image_id:
                ProductImage.create(image_vals)


    # product attributes for varient
    def sync_product_attributes(self, attribute_line, product_id):
        Attribute = self.env["product.attribute"]
        AttributeValue = self.env["product.attribute.value"]
        AttributeLine = self.env["product.template.attribute.line"]

        line_records = self.established_connection('product.template.attribute.line', 'search_read', [["id", "in", attribute_line]], False)
        done_attribute = []
        for line_rec in line_records:
            db_att_name = line_rec.get("attribute_id") 
            self_attribute = Attribute.search(
                [("name", "=", db_att_name[1])]
            )
            if not self_attribute:
                self_attribute = Attribute.create(
                    {"name": db_att_name[1]}
                )

            if db_att_name[0] not in done_attribute:
                done_attribute.append(db_att_name[0])
                db_att_value = self.established_connection('product.attribute.value', 'search_read', [["attribute_id", "=", db_att_name[0]]], False)
                
                for value in db_att_value:
                    self_att_value = AttributeValue.search([("name", "=", value.get("name")),("attribute_id", "=", self_attribute.id)])
                    if not self_att_value:
                        self_att_value = AttributeValue.create(
                            {
                                "name": value.get("name"),
                                "store_id": value.get('id'),
                                "attribute_id": self_attribute.id,
                            }
                        )
                    else:
                        self_att_value.write({'store_id': value.get('id')})

            db_att_value_ids = AttributeValue.search([('store_id', 'in', line_rec.get('value_ids'))]).ids

            # db_att_value_ids = []
            # for value_id in line_rec.get("value_ids"):
            #     db_att_value = self.established_connection('product.attribute.value', 'search_read', [["id", "=", value_id]], False)
            #     if db_att_value:
            #         self_att_value = AttributeValue.search(
            #             [
            #                 ("name", "=", db_att_value[0].get("name")),
            #                 ("attribute_id", "=", self_attribute.id),
            #             ]
            #         )
            #         if self_att_value:
            #             db_att_value_ids.append(self_att_value.id)
            #         if not self_att_value:
            #             self_att_value = AttributeValue.create(
            #                 {
            #                     "name": db_att_value[0].get("name"),
            #                     "attribute_id": self_attribute.id,
            #                 }
            #             )
            #             db_att_value_ids.append(self_att_value.id)

            AttributeLine.create(
                {
                    "product_tmpl_id": product_id.id,
                    "attribute_id": self_attribute.id,
                    "value_ids": [(6, 0, db_att_value_ids)],
                }
            )
    
    # get seller ids
    def get_varient_seller_ids(self, db_product, update_varients):
        Partner = self.env["res.partner"]
        SupplierInfo = self.env["product.supplierinfo"]
        get_seller_ids = []
        for seller_id in db_product.get("seller_ids"):
            db_seller_id = self.established_connection('product.supplierinfo', 'search_read', [["id", "=", seller_id]], False) 
            if db_seller_id:
                name = db_seller_id[0].get("name")
                partner = False
                if name:
                    partner = Partner.search([("name", "=", name[1])])
                    if not partner:
                        partner = Partner.create({"name": name[1],})
                supplier = SupplierInfo.create(
                    {
                        "name": partner.id,
                        "product_name": db_seller_id[0].get(
                            "product_name"
                        ),
                        "product_code": db_seller_id[0].get(
                            "product_code"
                        ),
                        "product_id": update_varients.id,
                        "min_qty": db_seller_id[0].get("min_qty"),
                        "price": db_seller_id[0].get("price"),
                    }
                )
                get_seller_ids.append(supplier.id)
        return get_seller_ids

    def sync_product_varient_update(self, db_product, product_tmpl_id):
        product_product_obj = self.env["product.product"]
        AttributeValue = self.env["product.template.attribute.value"]
        Quant = self.env["stock.quant"]

        # get default warehouse
        warehouse = self.env["stock.warehouse"].search(
            [("company_id", "=", self.env.company.id)], limit=1
        )

        db_product_varients = self.established_connection('product.product', 'search_read', [["product_tmpl_id", "=", db_product.get('id')]], False)                         
        for varient_rec in db_product_varients:
            self_varients = self.env["product.product"].search(
                [("product_tmpl_id", "=",product_tmpl_id.id)]
            )

            self_varients = self_varients.filtered(lambda x: x.partner_ref == varient_rec.get("partner_ref"))
            update_varients = self_varients.filtered(
                lambda x: x.partner_ref == varient_rec.get("display_name")
                and x.product_tmpl_id.id == product_tmpl_id.id
            )
            if not update_varients:
                varient_ref = varient_rec.get("display_name").split("] ")[1]
                update_varients = self_varients.filtered(lambda x: x.partner_ref == varient_ref and x.product_tmpl_id.id == product_tmpl_id.id)
            # elif not update_varients and varient_rec.get('attribute_line_ids'):
            #     # if varient_rec.get('id') == 11:
            #     #     import pdb;pdb.set_trace()
            #     combination = []
            #     for rec in varient_rec.get('attribute_line_ids'):
            #         att_val = self.established_connection('product.attribute.value', 'search_read', [["id", "=", rec]], False)
            #         print('\n\n\t\t\t    ===1111111111====       ', att_val[0].get('name'))
            #         if att_val and att_val[0]:
            #             self_att = self.env['product.template.attribute.value'].search([('name', '=', att_val[0].get('name'))], limit=1)
            #             print('\n\n\t\t\t    ====222222222===       ', self_att.name)
                        
            #             if self_att:
            #                 combination.append(self_att.id)
            #     update_varients = product_product_obj.search([('product_tmpl_id', '=', product_tmpl_id.id)]).filtered(
            #         lambda x: (x.attribute_line_ids.ids) == combination.sort()
            #     )

            # get seller ids
            get_seller_ids = []
            if db_product.get("seller_ids"):
                get_seller_ids = self.get_varient_seller_ids(db_product, update_varients)
                
            update_varients.update(
                {
                    "name": varient_rec.get("name"),
                    "type": varient_rec.get("type"),
                    "price": varient_rec.get("price"),
                    "lst_price": varient_rec.get("lst_price"),
                    "default_code": varient_rec.get("default_code"),
                    "code": varient_rec.get("code"),
                    "barcode": varient_rec.get("barcode"),
                    "standard_price": varient_rec.get("standard_price"),
                    "volume": varient_rec.get("volume"),
                    "weight": varient_rec.get("weight"),
                    "description": self.convert_html_to_text(
                        varient_rec.get("description", "")
                    ),
                    # "list_price": varient_rec.get("list_price"),
                    "volume_uom_name": varient_rec.get("volume_uom_name"),
                    "weight_uom_name": varient_rec.get("weight_uom_name"),
                    "image_variant_1920": varient_rec.get(
                        "image_variant_1920"
                    ),
                    "description_sale": self.convert_html_to_text(
                        db_product.get("description_sale", "")
                    ),
                    "is_published": db_product.get("is_published"),
                    "description_pickingin": self.convert_html_to_text(
                        db_product.get("description_pickingin", "")
                    ),
                    "seller_ids": [(6, 0, get_seller_ids)]
                }
            )

            for varient in varient_rec.get("product_template_attribute_value_ids"):
                att_value = self.established_connection("product.template.attribute.value", 'search_read', [["id", "=", varient]], False)                         
                att_val = AttributeValue.search([("product_tmpl_id", "=", product_tmpl_id.id),("name", "=", att_value[0].get("name"))])
                self_att_val = att_val.filtered(lambda x: x.display_name == att_value[0].get("display_name"))
                if self_att_val:
                    self_att_val.price_extra = att_value[0].get(
                        "price_extra"
                    )
            # qty according to varient
            if (
                varient_rec.get("qty_available")
                and update_varients
                and update_varients.type == "product"
            ):
                Quant.with_context(
                    inventory_mode=True
                ).create(
                    {
                        "product_id": update_varients.id,
                        "location_id": warehouse.lot_stock_id.id,
                        "inventory_quantity": varient_rec.get(
                            "qty_available"
                        ),
                    }
                )

    def action_product_sync(self):
        product_obj = self.env["product.template"]
        Category = self.env['product.public.category']
        ProductImage = self.env['product.image']
        Product = self.env['product.product']
        Quant = self.env["stock.quant"]

        # get default warehouse
        warehouse = self.env["stock.warehouse"].search([("company_id", "=", self.env.company.id)], limit=1)

        count = 0
        counter = 1
        while True:
            products = self.established_connection('product.template', 'search_read', [['id', '=', 2087]], {'limit': 100, 'order':'id Asc'})
            if products:
                for product in products:
                    category_id = False
                    if product.get("categ_id") and product["categ_id"][1]:
                        category_id = self.get_product_category(product["categ_id"]).id
                    
                    public_categ_ids = []
                    if product.get("public_categ_ids"):
                        public_categ_ids = Category.search([]).filtered(lambda l: int(l.store_id) in product['public_categ_ids']).ids
                        if not public_categ_ids:
                            self.sync_web_category()
                            public_categ_ids = Category.search([]).filtered(lambda l: int(l.store_id) in product['public_categ_ids']).ids

                    alternative_product_ids = []
                    if product.get("alternative_product_ids"):
                        alternative_product_ids = product_obj.search([]).filtered(lambda l: int(l.store_id) in product['alternative_product_ids']).ids
                    
                    product_image_ids = []
                    if product.get("product_template_image_ids"):
                        product_image_ids = ProductImage.search([]).filtered(lambda l: int(l.store_id) in product['product_template_image_ids']).ids
                        if not product_image_ids:
                            self.sync_web_product_images(product)
                            product_image_ids = ProductImage.search([]).filtered(lambda l: int(l.store_id) in product['product_template_image_ids']).ids

                    product_vals = {
                            "product_qnique_id": product['id'],
                            "name": product.get("name"),
                            "type": product.get("type"),
                            "list_price": product.get("list_price"),
                            "lst_price": product.get("lst_price"),
                            "default_code": product.get("default_code"),
                            "description": self.convert_html_to_text(product.get("description", "")),
                            "price": product.get("price"),
                            "standard_price": product.get("standard_price"),
                            "volume": product.get("volume"),
                            "volume_uom_name": product.get("volume_uom_name"),
                            "weight": product.get("weight"),
                            "weight_uom_name": product.get("weight_uom_name"),
                            "website_description": product.get("website_description"),
                            "uom_name": product.get("uom_name"),
                            "image_1920": product.get("image_1920"),
                            "description_sale": self.convert_html_to_text(product.get("description_sale", "")),
                            "website_published": product.get("website_published"),
                            "is_published": product.get("website_published"),
                            "description_pickingin": self.convert_html_to_text(product.get("description_picking", "")),
                            "categ_id": category_id,
                            "public_categ_ids": public_categ_ids,
                            "alternative_product_ids": alternative_product_ids,
                            "product_template_image_ids": product_image_ids,
                            "store_id": self.id,
                        }
                    
                    product_id = product_obj.search([('product_qnique_id', '=', product['id']), ('store_id', '=', self.id)])
                    if not product_id:
                        product_id = product_obj.create(product_vals)
                    else:
                        product_id.update(product_vals)

                    ''' Product attribute remove if it's removed from v10 DB '''
                    attribute_line = product.get("attribute_line_ids")
                    if not attribute_line:
                        varient_id = Product.search(
                            [("product_tmpl_id", "=", product_id.id)]
                        )
                        if (
                            varient_id
                            and varient_id.type == "product"
                            and product.get("qty_available")
                        ):
                            Quant.with_context(
                                inventory_mode=True
                            ).create(
                                {
                                    "product_id": varient_id.id,
                                    "location_id": warehouse.lot_stock_id.id,
                                    "inventory_quantity": product.get("qty_available"),
                                }
                            )
                    product_id.attribute_line_ids.unlink()

                    # get product attributes and values for varients
                    if attribute_line:
                        self.sync_product_attributes(attribute_line, product_id)

                    # Update product varient vals
                    self.sync_product_varient_update(product, product_id)
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", product.get('id'))
                    self._cr.commit()
                    print("//////////////////////////////counter", counter)
                    counter = counter + 1
                count = int(products[-1]['id'])
                break
            else:
                break
        if self._context.get("manual"):
            return {
                "name": "Message",
                "type": "ir.actions.act_window",
                "view_type": "form",
                "view_mode": "form",
                "res_model": "pop.message",
                "target": "new",
                "context": {
                    "default_name": "Products sychronisation process is completed!"
                },
            }
        else:
            return True

    def established_connection(self, obj, event, domain, limit):
        # try:
            url = self.url
            database = self.database
            username = self.username
            password = self.password
            url, db, username, password = url.strip(), database.strip(), username.strip(), password.strip()
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            uid = common.authenticate(db, username, password, {})
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            vals_tmpl = models.execute_kw(db, uid, password, 'product.template', 'search_read', [[['id', '=', '43542']]])
            vals = models.execute_kw(db, uid, password, obj, event, [domain], limit)
            return vals
        # except:
        #     raise ValidationError(_("The connection between two database is not established, look on the credentials you had filled and try again."))

class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    store_id = fields.Char(string="Store Id", readonly=True)

class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    store_id = fields.Char(string="Store Id", readonly=True)


class ProductImage(models.Model):
    _inherit = "product.image"

    store_id = fields.Char(string="Store Id", readonly=True)

class ProductTemplate(models.Model):
    _inherit = "product.template"

    store_id = fields.Many2one("product.sync", string="Store", readonly=True)


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_qnique_id = fields.Char(string="Product Store Id", readonly=True)
    store_id = fields.Many2one("product.sync", string="Store", readonly=True)


class ProductTemplateAttributeValue(models.Model):
    _inherit = "product.template.attribute.value"

    store_id = fields.Char(string="Store Id", readonly=True)


class IrCron(models.Model):
    _inherit = "ir.cron"

    store_id = fields.Many2one("product.sync", string="Store", readonly=True)

    def product_sync_crons(self):

        print("*"*240)
        print("\n\n\n\n\n\n\n\n\n\n\n\t\t\t\tCron started")
        print("*"*240)

        for rec in self.env['product.sync'].search([]):
            rec.action_product_sync()
            
        # now_datetime = datetime.datetime.now().strftime("%m/%d/%Y %H:%M")
        # crons = self.env["ir.cron"].search([])
        # if crons:
            # print("*"*240)
            # print("\n\n\n\n\n\n\n\n\n\n\n\t\t\t\tCron started")
            # print("*"*240)

        #     for cron in crons:
        #         if (
        #             cron
        #             and cron.nextcall.strftime("%m/%d/%Y %H:%M") == now_datetime
        #             and cron.store_id
        #         ):
        #             cron.store_id.action_product_sync()
