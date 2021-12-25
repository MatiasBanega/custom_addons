# -*- coding: utf-8 -*-

import csv
import logging
import base64
import traceback

from odoo import fields, models, _
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO


class ImportProducts(models.TransientModel):
    _name = "import.products"
    _description = "Product Import"

    file_path = fields.Binary(type="binary", string="File To Import")


    def _read_csv_data(self):
        """
        Reads CSV from given path and Return list of dict with Mapping
        """
        data = csv.reader(
            StringIO(base64.b64decode(self.file_path).decode("utf-8-sig")),
            quotechar='"',
            delimiter=",",
        )

        # Read the column names from the first line of the file
        fields = next(data)
        data_lines = []
        for row in data:
            items = dict(zip(fields, row))
            data_lines.append(items)
        return fields, data_lines

    def do_import_product_data(self):
        file_path = self.file_path
        if not file_path or file_path == "":
            _logger.warning(
                "Import can not be started. Upload your csv template"
            )
            return True
        fields = data_lines = False

        try:
            fields, data_lines = self._read_csv_data()
        except Exception as e:
            _logger.warning(
                "Can not read source file(csv), Invalid file path or File not reachable on file system. %s"
                % (e)
            )
            raise ValidationError(
                    _("Can not read source file(csv), Invalid file path or File not reachable on file system."))

        if not data_lines:
            _logger.info(
                "File has no data or it has been already imported, please update the file."
            )
            raise ValidationError(_("File has no data or it has been already imported, please update the file."))

        _logger.info(">>> Starting Import Packages Process from file.")

        product_product_obj = self.env["product.product"] 
        product_template_obj = self.env["product.template"] 

        attribute_value_ids = []
        public_categ_ids_ext = []
        current_processed_product = False
        need_to_go_new_line = False
        row = 2
        for data in data_lines:
            try:
                attribute_values = data['Attribute Values'] #product_template_attribute_value_ids
                internal_reference = data['Internal Reference'] #default_code
                product_name = data['Name']  #name
                #product_tags = data['Product Tags']
                product_type = data.get('Product Type', 'product') #type
                #brand = data.get('Brand')
                public_price = data['Public Price']   #lst_price
                cost_price = data['Cost']  #standard_price
                barcode = data['Barcode'] #barcode
                image = data['Image']  #image_1920
                #available_in_pos =  data['Available in POS'] #available_in_pos
                categ_id = data['Product Category/Complete Name']
                public_categ_ids = data['Website Product Category/Display Name']
                inventory_availability = data['Inventory Availability']
                extra_media_name = data['Extra Product Media/Name']
                extra_media_image = data['Extra Product Media/Image']
                description = data['Description']
                website_description = data['Description for the website']

                # if row == 150:
                #     a = 1/0

                if public_categ_ids:
                    split = public_categ_ids.split("/")
                    parent_id = False
                    if len(split) > 1:
                        parent_id = self.env['product.public.category'].search([
                            ('name','=', split[len(split)-2].strip())
                        ])
                        if not parent_id:
                            parent_id = self.env['product.public.category'].create({
                                'name': split[len(split)-2].strip()
                            })
                    domain = [('name','=',split[len(split) -1].strip())]
                    if parent_id:
                        domain.append(('parent_id','=',parent_id.id))
                    public_categ_ids = self.env['product.public.category'].search(domain)
                    if not public_categ_ids:
                        public_categ_ids = self.env['product.public.category'].create({
                                'name': split[len(split)-1].strip(),
                                'parent_id': parent_id and parent_id.id
                            })
                    public_categ_ids_ext.extend(public_categ_ids.ids)

                if self.is_attibute_lines(data):
                    #get attribute value object
                    attribute_value = self.get_attribute_id(attribute_values)

                    #process product template attribute
                    if attribute_value:
                        product_template_attribute_id = self.process_product_template_info(attribute_value, current_processed_product)
                        attribute_value_ids.append(product_template_attribute_id.id)
                    need_to_go_new_line = True

                if self.is_extra_media_images(data) and current_processed_product:
                    self.get_extra_images(extra_media_image, extra_media_name, current_processed_product)
                    need_to_go_new_line = True


                # _logger.info("******** %s", need_to_go_new_line)
                # _logger.info("******** %s", product_name)
                if need_to_go_new_line or not product_name:
                    row += 1
                    need_to_go_new_line = False
                    continue

                if public_categ_ids_ext and current_processed_product:
                    current_processed_product.write({
                        'public_categ_ids': [(4, x)  for x in public_categ_ids_ext]
                    })
                    public_categ_ids_ext = []

                if attribute_value_ids and current_processed_product:
                    _logger.info("******** product variant about to be created>>>>>")
                    product_product_obj.create({
                        'product_tmpl_id': current_processed_product.id,
                        'product_template_attribute_value_ids': [(4, x) for x in attribute_value_ids]
                    })
                    current_processed_product = False
                    _logger.info(">>>>>>>>>>>> %s", row)
                    attribute_value_ids = []

                if categ_id:
                    split = categ_id.split("/")
                    parent_id = False
                    if len(split) > 1:
                        parent_id = self.env['product.category'].search([
                            ('name','=', split[len(split)-2].strip())
                        ])
                        if not parent_id:
                            parent_id = self.env['product.category'].create({
                                'name': split[len(split)-2].strip()
                            })
                    domain = [('name','=',split[len(split) -1].strip())]
                    if parent_id:
                        domain.append(('parent_id','=',parent_id.id))
                    categ_id = self.env['product.category'].search(domain)
                    if not categ_id:
                        categ_id = self.env['product.category'].create({
                                'name': split[len(split)-1].strip(),
                                'parent_id': parent_id and parent_id.id
                            })


                vals = {
                    'name': product_name,
                    'type': product_type or 'product',
                    'default_code': internal_reference,
                    'lst_price': public_price,
                    'standard_price': cost_price,
                    'image_1920': image,
                    'website_description': website_description,
                    'description': description,
                    'inventory_availability': inventory_availability,
                    #'product_template_image_ids': product_template_image_ids,
                    #'available_in_pos': available_in_pos,
                }
                if barcode:
                    vals['barcode'] = barcode
                if categ_id:
                    vals['categ_id'] = categ_id and categ_id.id
                
                _logger.info("****** product template about to be created >>>>>")
                current_processed_product = product_template_obj.with_context(skip_varient=True).create(vals)

                #get attribute value object
                attribute_value = self.get_attribute_id(attribute_values)

                #get extra media images
                self.get_extra_images(extra_media_image, extra_media_name, current_processed_product)

                #process product template attribute
                if attribute_value:
                    product_template_attribute_id = self.process_product_template_info(attribute_value, current_processed_product)
                    attribute_value_ids.append(product_template_attribute_id.id)

            except Exception as e:
                traceback.print_exc()
                raise ValidationError(_("Row: %s Error: %s") %(row, e))
            row += 1
        #incase of trailing data
        if public_categ_ids_ext and current_processed_product:
            current_processed_product.write({
                'public_categ_ids': [(4, x)  for x in public_categ_ids_ext]
            })
            public_categ_ids_ext = []

        if attribute_value_ids and current_processed_product:
            _logger.info("******** product variant about to be created at the end>>>>>")
            product_product_obj.create({
                'product_tmpl_id': current_processed_product.id,
                'product_template_attribute_value_ids': [(4, x) for x in attribute_value_ids]
            })
            current_processed_product = False
            attribute_value_ids = []

    def is_attibute_lines(self, data):
        return (not data["Name"] and not data["Public Price"]) and data['Attribute Values']

    def is_extra_media_images(self, data):
        return (not data["Name"] and not data["Public Price"]) and data["Extra Product Media/Image"]

    def get_attribute_id(self, info):
        #_logger.info("!!! getting attribute>")
        attribute_info = info.split(":")
        if len(attribute_info) > 1:
            attribute_id = self.env['product.attribute'].search([('name','=',attribute_info[0])], limit=1)
            if not attribute_id:
                return False
            attribute_value = self.env['product.attribute.value'].search([
                ('attribute_id','=',attribute_id.id),
                ('name','=',attribute_info[1])
                ], limit=1)
            if not attribute_value:
                attribute_value = self.env['product.attribute.value'].with_context(skip_varient=True).create({
                    'attribute_id': attribute_id.id,
                    'name': attribute_info[1]
                })
            return attribute_value
        return False

    def process_product_template_info(self, attribute_value, product):
        #_logger.info("@@@ adding product template attribute line and values>>>")
        # prod_temp_att_line = self.env['product.template.attribute.line'].search([
        #     ('attribute_id','=',attribute_value.attribute_id.id),
        #     ('product_tmpl_id','=',product.id),
        # ])
        prod_temp_att_line = False
        if not prod_temp_att_line:
            prod_temp_att_line = self.env['product.template.attribute.line'].with_context(skip_varient=True).create({
                'attribute_id': attribute_value.attribute_id.id,
                'product_tmpl_id': product.id,
                'value_ids': [(4, attribute_value.id)]
            })
        # if prod_temp_att_line.filtered(lambda r: attribute_value.id not in r.value_ids.ids):
        #     prod_temp_att_line.with_context(skip_varient=True).write({
        #         'value_ids': [(4, attribute_value.id)]
        #     })
        prod_temp_att_value = self.env['product.template.attribute.value'].search([
            ('attribute_line_id','=',prod_temp_att_line.id),
            ('product_attribute_value_id','=',attribute_value.id)
        ])
        if not prod_temp_att_value:
            prod_temp_att_value = self.env['product.template.attribute.value'].with_context(skip_varient=True).create({
                'attribute_line_id': prod_temp_att_line.id,
                'product_attribute_value_id': attribute_value.id
            })
        return prod_temp_att_value

    def get_extra_images(self, extra_media_image, extra_media_name, product):
        if extra_media_image:
            #_logger.info("****** adding extra images>>>>")
            return self.env['product.image'].with_context(skip_varient=True).create({
                'image_1920': extra_media_image,
                'name': extra_media_name or product.name,
                #'product_variant_id': product.id,
                'product_tmpl_id': product.id,
            })
        return False
