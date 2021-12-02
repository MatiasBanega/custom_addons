odoo.define('theme_prime.ajaxload', function (require) {
'use strict';

let {qweb} = require('web.core');
let publicWidget = require('web.public.widget');

publicWidget.registry.DrAjaxLoadProducts = publicWidget.Widget.extend({
    xmlDependencies: ['/theme_prime/static/src/xml/core/snippet_root_widget.xml'],
    selector: '#products_grid',
    /**
     * @override
     */
    start: function () {
        var self = this;
        var defs = [this._super.apply(this, arguments)];
        this.ajaxEnabled = odoo.dr_theme_config.bool_enable_ajax_load;
        this.$pager = $('.products_pager');
        this.$tpRTargetElement = $('#wrapwrap'); // #wrapwrap for now bcoz window is not scrolleble in v14
        if (this.ajaxEnabled && this.$pager.children().length && this.$('.o_wsale_products_grid_table_wrapper tbody tr:last').length) {
            this.$pager.addClass('d-none');
            this._setState();
            var position = this.$tpRTargetElement.scrollTop();
            this.$tpRTargetElement.on('scroll.ajax_load_product', _.throttle(function (ev) {
                var scroll = self.$tpRTargetElement.scrollTop();
                if (scroll > position) {
                    // Trigger only when scrollDown
                    self._onScrollEvent(ev);
                }
                position = scroll;
            }, 20));
        }
        return Promise.all(defs);
    },
    _setState: function () {
        this.$lastLoadedProduct = this.$('.o_wsale_products_grid_table_wrapper tbody tr:last');
        this.$productsContainer = this.$('.o_wsale_products_grid_table_wrapper tbody');
        this.readyNextForAjax = true;
        this.pageURL = this.$pager.find('li:last a').attr('href');
        this.lastLoadedPage = 1;
        this.totalPages = parseInt(this.$target.get(0).dataset.totalPages);
    },
    _onScrollEvent: function (ev) {
        var self = this;
        if (this.$lastLoadedProduct.offset().top - this.$tpRTargetElement.scrollTop() + this.$lastLoadedProduct.height() < this.$tpRTargetElement.height() - 25 && this.readyNextForAjax && this.totalPages > this.lastLoadedPage) {
            this.readyNextForAjax = false;
            var newPage = self.lastLoadedPage + 1;
            $.ajax({
                url: this.pageURL,
                type: 'GET',
                beforeSend: function () {
                    $(qweb.render('droggol_default_loader')).appendTo(self.$('.o_wsale_products_grid_table_wrapper'));
                },
                success: function (page) {
                    self.$('.d_spinner_loader').remove();
                    let $renderedPage = $(page);
                    let $productsToAdd = $renderedPage.find("#products_grid .o_wsale_products_grid_table_wrapper table tr");
                    self.$productsContainer.append($productsToAdd);
                    self.readyNextForAjax = true;
                    self.$lastLoadedProduct = self.$('.o_wsale_products_grid_table_wrapper tbody tr:last');
                    self.lastLoadedPage = newPage;
                    self.pageURL = $renderedPage.find('.products_pager li:last a').attr('href');
                    if ($renderedPage.find('.products_pager li:last').hasClass('disabled')) {
                        $(qweb.render('dr_all_products_loaded')).appendTo(self.$('.o_wsale_products_grid_table_wrapper'));
                    }
                    self.trigger_up('widgets_start_request', {
                        $target: $('.tp-product-quick-view-action'),
                    });
                    self.trigger_up('widgets_start_request', {
                        $target: $('.tp_show_similar_products'),
                    });
                }
            });
        }
    },
});

});
