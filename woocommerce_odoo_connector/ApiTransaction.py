import itertools
import logging 
_logger = logging.getLogger(__name__)
from odoo import fields
from odoo.exceptions import UserError
from odoo.addons.odoo_multi_channel_sale.ApiTransaction import METAMAP
from odoo.addons.odoo_multi_channel_sale.ApiTransaction import Transaction

def split_seq(iterable, size):
    it = iter(iterable)
    item = list(itertools.islice(it, size))
    while item:
        yield item
        item = list(itertools.islice(it, size))


class WoocommerceTransaction:
    def __init__(self, channel, *args, **kwargs):
        self.instance = channel
        self.channel = channel.channel
        self.env = channel.env
        self._cr = channel._cr
        self.evaluate_feed = channel.auto_evaluate_feed
        self.display_message = channel.display_message

    def woocommerce_import_data(self, object, **kw):
        msg = "Current channel doesn't allow it."
        success_ids = []
        error_ids   = []
        create_ids  = []
        update_ids  = []
        if hasattr(self.instance,'import_{}'.format(self.channel)):
            msg = ''
            try:
                while True:
                    feeds = False
                    data_list, kw = getattr(
                        self.instance, 'import_{}'.format(self.channel))(object, **kw), kw
                    kw = data_list[1] if isinstance(data_list, tuple) else kw
                    data_list = [] if data_list == None else data_list[0]
                    if data_list:
                        kw['last_id'] = data_list[-1].get('store_id')
                        if object == 'product.category':
                            s_ids,e_ids,feeds = self.env['category.feed'].with_context(
                                channel_id=self.instance
                            )._create_feeds(data_list)
                        elif object == 'product.template':
                            s_ids,e_ids,feeds = self.env['product.feed'].with_context(
                                channel_id=self.instance
                            )._create_feeds(data_list)
                        elif object == 'res.partner':
                            s_ids,e_ids,feeds = self.env['partner.feed'].with_context(
                                channel_id=self.instance
                            )._create_feeds(data_list)
                        elif object == 'sale.order':
                            s_ids,e_ids,feeds = self.env['order.feed'].with_context(
                                channel_id=self.instance
                            )._create_feeds(data_list)
                        elif object == 'delivery.carrier':
                            s_ids, e_ids, feeds = self.env['shipping.feed'].with_context(
                                channel_id=self.instance
                            )._create_feeds(data_list)
                        else:
                            raise Exception('Invalid object type')

                        self._cr.commit()
                        _logger.info(f'~~~~{len(s_ids)} feeds committed~~~~')
                        _logger.info(f"~~~~Latest Id: {kw.get('last_id')}~~~~")
                        success_ids.extend(s_ids)
                        error_ids.extend(e_ids)
                        if self.evaluate_feed and feeds:
                            mapping_ids = feeds.with_context(get_mapping_ids=True).import_items()
                            create_ids.extend([mapping.id for mapping in mapping_ids.get('create_ids')])
                            update_ids.extend([mapping.id for mapping in mapping_ids.get('update_ids')])
                            self._cr.commit()
                            _logger.info('~~~~Created feeds are evaluated~~~~')
                        if kw.get("woocommerce_import_date_from"):
                            self.set_woocommerce_cron_date(kw["last_added"],object)
                    if len(data_list)<1 or kw.get("woocommerce_object_id"):
                        break
                    kw["page_number"]  += 1            
            except Exception as e:
                msg = f'Something went wrong: `{e.args[0]}`'
                _logger.exception(msg)

            if not msg:
                if success_ids:
                    msg += f"<p style='color:green'>{success_ids} imported.</p>"
                if error_ids:
                    msg += f"<p style='color:red'>{error_ids} not imported.</p>"
                if create_ids:
                    msg += f"<p style='color:blue'>{create_ids} created.</p>"
                if update_ids:
                    msg += f"<p style='color:blue'>{update_ids} updated.</p>"
                if kw.get('last_id'):
                    msg+= f"<p style='color:brown'>Last Id: {kw.get('last_id')}.</p>"
            if not msg:
                msg="<p style='color:red'>No records found for applied filter.</p>"
        return self.display_message(msg)
    
    def set_woocommerce_cron_date(self, date_created, object):
        date_created = fields.Datetime.to_datetime(" ".join(date_created.split("T")))
        if object == "product.template":
            self.instance.import_product_date = date_created
        elif object == "sale.order":
            self.instance.import_order_date = date_created
        elif object == "res.partner":
            self.instance.import_customer_date = date_created

    def woocommerce_export_data(self, object, object_ids, operation='export'):
        transaction = Transaction(self.instance)
        create_mapping = transaction.create_mapping
        get_remote_id  = transaction.get_remote_id
        msg = "Selected Channel doesn't allow it."
        success_ids, error_ids  = [], []

        mappings = self.env[METAMAP.get(object).get('model')].search(
            [
                ('channel_id','=',self.instance.id),
                (
                    METAMAP.get(object).get('local_field'),
                    'in',
                    object_ids
                ),
            ]
        )

        if operation == 'export' and hasattr(self.instance,'export_{}'.format(self.channel)):
            msg = ''
            local_ids = mappings.mapped(
                lambda mapping: int(getattr(mapping,METAMAP.get(object).get('local_field')))
            )
            local_ids = set(object_ids)-set(local_ids)
            if not local_ids:
                return self.display_message(
                    """<p style='color:orange'>
                        Selected records have already been exported.
                    </p>"""
                )
            operation = 'exported'
            local_ids = split_seq(local_ids,self.instance.api_record_limit)
            for local_id in local_ids:
                for record in self.env[object].browse(local_id):
                    res,remote_object = getattr(self.instance,'export_{}'.format(self.channel))(record)
                    if res:
                        create_mapping(record,remote_object)
                        success_ids.append(record.id)
                    else:
                        error_ids.append(record.id)
                self._cr.commit()

        elif operation == 'update' and hasattr(self.instance,'update_{}'.format(self.channel)):
            msg = ''
            local_ids = mappings.filtered_domain([
                ('need_sync', '=', 'yes')]).mapped(
                lambda mapping: int(getattr(mapping,METAMAP.get(object).get('local_field')))
            )
            if not local_ids:
                if mappings:
                    return self.display_message(
                        """<p style='color:orange'>
                            Nothing to update on selected records.
                        </p>"""
                    )
                else:
                    return self.display_message(
                        """<p style='color:orange'>
                            Selected records haven't been exported yet.
                        </p>"""
                    )
            operation = 'updated'
            local_ids = split_seq(local_ids,self.instance.api_record_limit)
            for local_id in local_ids:
                for record in self.env[object].browse(local_id):
                    res,remote_object = getattr(self.instance,'update_{}'.format(self.channel))(
                        record = record,
                        get_remote_id = get_remote_id
                    )
                    if res:
                        success_ids.append(record.id)
                    else:
                        error_ids.append(record.id)
                self._cr.commit()

        self.env[METAMAP.get(object).get('model')].search([
                ('channel_id','=',self.instance.id),
                (
                    METAMAP.get(object).get('local_field'),
                    'in',
                    success_ids
                )]).write({'need_sync': 'no'})

        if not msg:
            if success_ids:
                msg += f"<p style='color:green'>{success_ids} {operation}.</p>"
            if error_ids:
                msg += f"<p style='color:red'>{error_ids} not {operation}.</p>"
        return self.display_message(msg)

