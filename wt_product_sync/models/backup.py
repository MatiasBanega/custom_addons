# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import AccessError
from html.parser import HTMLParser
from xmlrpc import client as xmlrpclib
import datetime
import re


class HTMLFilter(HTMLParser):
    text = ""

    def handle_data(self, data):
        self.text += data


class ProductSync(models.Model):
    _name = "product.sync"
    _description = "Product Store"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        string="Store Name",
        required=True,
        tracking=1,
        help="Store Name you would like to have",
    )
    url = fields.Char(
        string="Url",
        tracking=1,
        help="url of database you want to fetch data http://warlocktechnologies.com",
        required=True,
    )
    database = fields.Char(
        string="Database",
        tracking=1,
        help="database name of the target url",
        required=True,
    )
    username = fields.Char(
        string="User Name",
        tracking=1,
        help="admin user name of target url",
        required=True,
    )
    password = fields.Char(
        string="Password",
        tracking=0,
        help="password of user name of target url",
        required=True,
    )
    active = fields.Boolean(default=True)
    interval_number = fields.Integer(default=1, help="Repeat every x.")
    interval_type = fields.Selection(
        [
            ("minutes", "Minutes"),
            ("hours", "Hours"),
            ("days", "Days"),
            ("weeks", "Weeks"),
            ("months", "Months"),
        ],
        string="Interval Unit",
        default="months",
    )
    cron_id = fields.Many2one("ir.cron", "Cron Id", readonly=True)
    product_ids_history = fields.Text(string="Product ID History")

    @api.model
    def create(self, vals):
        res = super(ProductSync, self).create(vals)
        if res:
            ir_model = self.env["ir.model"].sudo().search([("model", "=", res._name)])
            date = datetime.datetime.now() + datetime.timedelta(minutes=2)
            cron = self.env["ir.cron"].create(
                {
                    "name": "[" + res.name + "]" + " : Sync Product data",
                    "model_id": ir_model.id,
                    "state": "multi",
                    "interval_number": res.interval_number,
                    "interval_type": res.interval_type,
                    "active": True,
                    "numbercall": -1,
                    "store_id": res.id,
                    "nextcall": date,
                }
            )
            res.cron_id = cron.id
        return res

    def write(self, vals):
        res_update = super(ProductSync, self).write(vals)
        if vals.get("name"):
            self.cron_id.name = "[" + vals.get("name") + "]" + " : Sync Product data"
        if vals.get("interval_number"):
            self.cron_id.interval_number = vals.get("interval_number")
        if vals.get("interval_type"):
            self.cron_id.interval_type = vals.get("interval_type")
        return res_update

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

    def action_sync(self):
        # try:
        url = self.url
        database = self.database
        username = self.username
        password = self.password
        url, db, username, password = (
            'http://%s/xmlrpc/' % (url).strip(),
            database.strip(),
            username.strip(),
            password.strip(),
        )
        common = xmlrpclib.ServerProxy(url+'common')
        models = xmlrpclib.ServerProxy(url+'object')
        uid = common.login(db,username,password)
        product_obj = self.env["product.template"]
        attribute_obj = self.env["product.attribute"]
        product_product_obj = self.env["product.product"]
        tmpl_attribute_line_obj = self.env["product.template.attribute.line"]
        attribute_value_obj = self.env["product.attribute.value"]
        product_category_obj = self.env["product.category"]
        category_obj = self.env['product.public.category']
        stock_quant_obj = self.env["stock.quant"]
        res_partner_obj = self.env["res.partner"]
        product_supplierinfo_obj = self.env["product.supplierinfo"]
        p_t_attribute_value = self.env["product.template.attribute.value"]
        warehouse = self.env["stock.warehouse"].search(
            [("company_id", "=", self.env.company.id)], limit=1
        )
        list_ids = []
        if self.product_ids_history:
            temp = re.findall(r"\d+", self.product_ids_history)
            result_ids = list(map(int, temp))
            list_ids += result_ids
            db_products = models.execute_kw(
                db,
                uid,
                password,
                "product.template",
                "search_read",
                [[["id", "not in", result_ids]]],
                {"limit": 50},
            )
        else:
            db_products = models.execute_kw(
                db,
                uid,
                password,
                "product.template",
                "search_read",
                [[["name", "!=", False]]],
                {"limit": 50},
            )
        if db_products:
            for db_product in db_products:
                list_ids.append(db_product.get("id"))
                values = {
                    "name": db_product.get("name"),
                    "type": db_product.get("type"),
                    "lst_price": db_product.get("lst_price"),
                    "default_code": db_product.get("default_code"),
                    "description": self.convert_html_to_text(
                        db_product.get("description", "")
                    ),
                    "price": db_product.get("price"),
                    "standard_price": db_product.get("standard_price"),
                    "volume": db_product.get("volume"),
                    "volume_uom_name": db_product.get("volume_uom_name"),
                    "weight": db_product.get("weight"),
                    "weight_uom_name": db_product.get("weight_uom_name"),
                    "uom_name": db_product.get("uom_name"),
                    "image_1920": db_product.get("image_medium"),
                    "description_sale": self.convert_html_to_text(
                        db_product.get("description_sale", "")
                    ),
                    "website_published": db_product.get("website_published"),
                    "is_published": db_product.get("website_published"),
                    "description_pickingin": self.convert_html_to_text(
                        db_product.get("description_picking", "")
                    ),
                }
                sync_unique_id = str(self.id) + str(db_product.get("id"))
                product_tmpl_id = product_obj.search(
                    [("product_qnique_id", "=", sync_unique_id)]
                )
                if not product_tmpl_id:
                    product_tmpl_id = product_obj.create(values)
                    product_tmpl_id.product_qnique_id = sync_unique_id
                    product_tmpl_id.store_id = self.id
                else:
                    product_tmpl_id.write(values)
                    
                product_tmpl_id.list_price = db_product.get("list_price")
                # Product Category
                if db_product.get("categ_id")[1]:
                    db_categ = db_product.get("categ_id")
                    category = db_categ[1].split("/")
                    categ_id = False
                    parent_id = [0]
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
                        else:
                            pass
                        parent_id[0] = categ_id.id
                    product_tmpl_id.categ_id = categ_id.id
                   
                # Website Categories
                categ_ids = []
                if db_product.get('public_categ_ids'):
                    for rec_id in db_product.get('public_categ_ids'):
                            db_public_categ_ids = models.execute_kw(db, uid, password,
                                                                    'product.public.category', 'search_read',
                                                                    [[['id', '=', rec_id]]])
                            category = db_public_categ_ids[0].get('display_name').split('/')
                            public_categ_ids = category_obj.search([('name', '=', self.name)])
                            if not public_categ_ids:
                                public_categ_ids = category_obj.create({
                                    'name': self.name,
                                })
                            parent_id = [0]
                            for catg_len in range(len(category)):
                                public_categ_id = category_obj.search([('name', '=', category[catg_len].strip())])
                                if not public_categ_id:
                                    public_categ_id = category_obj.create({
                                        'name': category[catg_len].strip()
                                    })
                                is_categ = category_obj.search([('id', '=', parent_id[0])])
                                if is_categ:
                                    public_categ_id.parent_id = is_categ.id
                                else:
                                    pass
                                parent_id[0] = public_categ_id.id
                            categ_ids.append(public_categ_id.id)
                            product_tmpl_id.write({
                                'public_categ_ids': [(6, 0, categ_ids)]
                            })

                # Website Alternative Products  
                alternative_products = []
                if db_product.get('alternative_product_ids'):
                    for a_p_i in db_product.get('alternative_product_ids'):
                        unique_p_id = str(self.id) + str(a_p_i)
                        alternative_p_id = product_obj.search([('product_qnique_id', '=',unique_p_id)])
                        alternative_products.append(alternative_p_id.id)
                product_tmpl_id.write({
                    'alternative_product_ids': [(6, 0, alternative_products)]
                })

                # Website accessory Products  
                # accessory_product_ids = []
                # # product_tmpl_id
                # if db_product.get('alternative_product_ids'):
                #     for a_p_i in db_product.get('alternative_product_ids'):
                #         unique_p_id = str(self.id) + str(a_p_i)
                #         alternative_p_id = product_obj.search([('product_qnique_id', '=',unique_p_id)])
                #         alternative_products.append(alternative_p_id.id)
                # product_tmpl_id.write({
                #     'alternative_product_ids': [(6, 0, alternative_products)]
                # })


                product_tmpl_id.product_template_image_ids.unlink()
                db_tmpl_image_ids = db_product.get("product_template_image_ids")
                if db_tmpl_image_ids:
                    for image in db_tmpl_image_ids:
                        db_tmpl_image_id = models.execute_kw(
                            db,
                            uid,
                            password,
                            "product.image",
                            "search_read",
                            [[["id", "=", image]]],
                        )
                        if db_tmpl_image_id:
                            product_tmpl_id.write(
                                {
                                    "product_template_image_ids": [
                                        (
                                            0,
                                            0,
                                            {
                                                "name": db_tmpl_image_id[0].get("name"),
                                                "image_1920": db_tmpl_image_id[0].get(
                                                    "image_medium"
                                                ),
                                            },
                                        )
                                    ]
                                }
                            )
                db_tmpl_attribute_line = db_product.get("attribute_line_ids")

                if not db_tmpl_attribute_line:
                    product_tmpl_id.barcode = db_product.get("barcode")
                    varient_id = product_product_obj.search(
                        [("product_tmpl_id", "=", product_tmpl_id.id)]
                    )
                    if (
                        varient_id
                        and varient_id.type == "product"
                        and db_product.get("qty_available")
                    ):
                        stock_quant_obj.with_context(
                            inventory_mode=True
                        ).create(
                            {
                                "product_id": varient_id.id,
                                "location_id": warehouse.lot_stock_id.id,
                                "inventory_quantity": db_product.get("qty_available"),
                            }
                        )

                product_tmpl_id.attribute_line_ids.unlink()

                if db_tmpl_attribute_line:
                    for tmpl_attribute_line in db_tmpl_attribute_line:
                        db_tmpl_line = models.execute_kw(
                            db,
                            uid,
                            password,
                            "product.attribute.line",
                            "search_read",
                            [[["id", "=", tmpl_attribute_line]]],
                        )

                        if db_tmpl_line:

                            db_att_name = db_tmpl_line[0].get("attribute_id")
                            self_attribute = attribute_obj.search(
                                [("name", "=", db_att_name[1])]
                            )
                            if not self_attribute:
                                self_attribute = attribute_obj.create(
                                    {"name": db_att_name[1]}
                                )
                            db_att_value_ids = []
                            for value_id in db_tmpl_line[0].get("value_ids"):
                                db_att_value = models.execute_kw(
                                    db,
                                    uid,
                                    password,
                                    "product.attribute.value",
                                    "search_read",
                                    [[["id", "=", value_id]]],
                                )
                                if db_att_value:
                                    self_att_value = attribute_value_obj.search(
                                        [
                                            ("name", "=", db_att_value[0].get("name")),
                                            ("attribute_id", "=", self_attribute.id),
                                        ]
                                    )
                                    if self_att_value:
                                        db_att_value_ids.append(self_att_value.id)
                                    if not self_att_value:
                                        self_att_value = attribute_value_obj.create(
                                            {
                                                "name": db_att_value[0].get("name"),
                                                "attribute_id": self_attribute.id,
                                            }
                                        )
                                        db_att_value_ids.append(self_att_value.id)

                            varients_idd = tmpl_attribute_line_obj.create(
                                {
                                    "product_tmpl_id": product_tmpl_id.id,
                                    "attribute_id": self_attribute.id,
                                    "value_ids": [(6, 0, db_att_value_ids)],
                                }
                            )

                    db_product_varients = models.execute_kw(
                        db,
                        uid,
                        password,
                        "product.product",
                        "search_read",
                        [[["product_tmpl_id", "=", db_product.get("id")]]],
                    )
                    
                    for varient_rec in db_product_varients:

                        # test = product_product_obj.search(
                        #     [("id", "=", "350")]
                        # )
                        # print('\n\n\n\n\n\n\n\t\t\t\t\t\t\t  ----test-----         ', test.read())
                        # print('\n\n\n\n\n\n\n\t\t\t\t\t\t\t  ----display_name-----         ', varient_rec.get("display_name"))
                        self_varients = product_product_obj.search(
                            [("partner_ref", "=", varient_rec.get("display_name"))]
                        )
                        update_varients = self_varients.filtered(
                            lambda x: x.partner_ref == varient_rec.get("display_name")
                            and x.product_tmpl_id.id == product_tmpl_id.id
                        )
                        if not update_varients:
                            varient_ref = varient_rec.get("display_name").split("] ")[1]
                            update_varients = self_varients.filtered(
                                lambda x: x.partner_ref == varient_ref
                                and x.product_tmpl_id.id == product_tmpl_id.id
                            )
                        # print('\n\n\n\n\n\n\n\t\t\t\t\t\t\t  ----update_varients-----         ', update_varients)
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
                                "list_price": varient_rec.get("list_price"),
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
                            }
                        )

                        get_seller_ids = []
                        if db_product.get("seller_ids"):
                            for seller_id in db_product.get("seller_ids"):
                                db_seller_id = models.execute_kw(
                                    db,
                                    uid,
                                    password,
                                    "product.supplierinfo",
                                    "search_read",
                                    [[["id", "=", seller_id]]],
                                )
                                if db_seller_id:
                                    name = db_seller_id[0].get("name")
                                    partner = False
                                    if name:
                                        partner = res_partner_obj.search(
                                            [("name", "=", name[1])]
                                        )
                                        if not partner:
                                            partner = res_partner_obj.create(
                                                {
                                                    "name": name[1],
                                                }
                                            )
                                    supplier = product_supplierinfo_obj.create(
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
                        update_varients.write({"seller_ids": [(6, 0, get_seller_ids)]})

                        for varient in varient_rec.get("attribute_value_ids"):
                            att_value = models.execute_kw(
                                db,
                                uid,
                                password,
                                "product.attribute.value",
                                "search_read",
                                [[["id", "=", varient]]],
                            )
                            self_att_val = p_t_attribute_value.search(
                                [
                                    ("product_tmpl_id", "=", product_tmpl_id.id),
                                    ("name", "=", att_value[0].get("name")),
                                    (
                                        "display_name",
                                        "=",
                                        att_value[0].get("display_name"),
                                    ),
                                ]
                            )
                            if self_att_val:
                                self_att_val.price_extra = att_value[0].get(
                                    "price_extra"
                                )

                        if (
                            varient_rec.get("qty_available")
                            and update_varients
                            and update_varients.type == "product"
                        ):
                            stock_quant_obj.with_context(
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
            if list_ids:
                self.write({"product_ids_history": list_ids})
        else:
            self.write({"product_ids_history": ""})
        # except:
        #     raise AccessError(_("[Errno 111] Connection refused"))


class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_qnique_id = fields.Char(string="Store Id", readonly=True)
    store_id = fields.Many2one("product.sync", string="Store", readonly=True)


class IrCron(models.Model):
    _inherit = "ir.cron"

    store_id = fields.Many2one("product.sync", string="Store", readonly=True)

    def product_sync_crons(self):
        now_datetime = datetime.datetime.now().strftime("%m/%d/%Y %H:%M")
        crons = self.env["ir.cron"].search([])
        if crons:
            for cron in crons:
                if (
                    cron
                    and cron.nextcall.strftime("%m/%d/%Y %H:%M") == now_datetime
                    and cron.store_id
                ):
                    cron.store_id.action_sync()
