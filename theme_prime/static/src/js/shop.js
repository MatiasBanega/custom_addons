odoo.define('theme_prime.shop', function (require) {
'use strict';

const publicWidget = require('web.public.widget');
const { _t } = require('web.core');

publicWidget.registry.TpSelectedAttributes = publicWidget.Widget.extend({
    selector: '.tp-selected-attributes',
    events: {
        'click .tp-attribute': '_onClickAttribute'
    },
    _onClickAttribute: function (ev) {
        const $form = $('.js_attributes');
        const type = $(ev.currentTarget).data('type');
        if (type === 'price') {
            $form.find('input[name=min_price]').remove();
            $form.find('input[name=max_price]').remove();
            $form.submit();
        } else if (type === 'attribute') {
            const $input = $form.find('input[value=' + $(ev.currentTarget).data('id') + ']');
            $input.prop('checked', false);
            const $select = $form.find('option[value=' + $(ev.currentTarget).data('id') + ']').closest('select');
            $select.val('');
            $form.submit();
        } else if (type === 'brand') {
            const $input = $form.find('input[name=brand][value=' + $(ev.currentTarget).data('id') + ']');
            $input.prop('checked', false);
            $form.submit();
        } else if (type === 'label') {
            const $input = $form.find('input[name=label][value=' + $(ev.currentTarget).data('id') + ']');
            $input.prop('checked', false);
            $form.submit();
        } else if (type === 'tag') {
            const $input = $form.find('input[name=tag][value=' + $(ev.currentTarget).data('id') + ']');
            $input.prop('checked', false);
            $form.submit();
        } else if (type === 'rating') {
            const $input = $form.find('input[name=rating][value=' + $(ev.currentTarget).data('id') + ']');
            $input.prop('checked', false);
            $form.submit();
        }
    },
});

publicWidget.registry.TpFilterSidebar = publicWidget.Widget.extend({
    selector: '.o_wsale_products_main_row',
    init: function () {
        this._super.apply(this, arguments);
        this.$backdrop = $('<div class="modal-backdrop tp-sidebar-backdrop show d-block"/>');
        // Binding event here bcz it's in oe_website_sale scope, and quick view refresh animation for oe_website_sale, so it's rebinding events again.
        $('.tp-filter-sidebar-toggle').on('click', this._onClickToggleSidebar.bind(this));
        $('.tp-filter-bottom-sidebar-toggle').on('click', this._onClickToggleSidebar.bind(this));
    },
    _onClickToggleSidebar: function (ev) {
        ev.preventDefault();
        if (this.$('#products_grid_before').hasClass('open')) {
            this.$backdrop.remove();
            this.$('#products_grid_before').removeClass('open');
            $('#wrapwrap').css('z-index', 0);
            $('body').removeClass('modal-open');
        } else {
            this.$backdrop.appendTo('body');
            this.$('#products_grid_before').addClass('open');
            $('#wrapwrap').css('z-index', 'unset');
            $('body').addClass('modal-open');
            this.$backdrop.on('click', this._onClickToggleSidebar.bind(this));
        }
        this.$('.tp-filter-sidebar-item').toggleClass('show d-none');
    },
});

publicWidget.registry.TpFilterAttribute = publicWidget.Widget.extend({
    selector: '.tp-filter-attribute',
    events: {
        'input .tp-search': '_onChangeSearch',
        'click .tp-filter-attribute-title.collapsible': '_onClickFilterAttributeTitle',
    },
    _onChangeSearch: function (ev) {
        ev.stopPropagation();
        const value = $(ev.currentTarget).val().trim();
        if (value) {
            this.$('li[data-search-term]').addClass('d-none');
            this.$('li[data-search-term*="' + value.toLowerCase() + '"]').removeClass('d-none');
        } else {
            this.$('li[data-search-term]').removeClass('d-none');
        }
    },
    _onClickFilterAttributeTitle: function (ev) {
        if ($(ev.currentTarget).hasClass('expanded')) {
            $(ev.currentTarget).siblings('.tp-filter-attribute-collapsible-area').slideUp('fast');
        } else {
            $(ev.currentTarget).siblings('.tp-filter-attribute-collapsible-area').slideDown('fast');
        }
        $(ev.currentTarget).toggleClass('expanded');
    },
});

publicWidget.registry.TpPriceFilter = publicWidget.Widget.extend({
    selector: '.tp-price-filter',
    events: {
        'change input.min_price': '_onChangePrice',
        'change input.max_price': '_onChangePrice',
        'click .apply': '_onClickApply',
    },
    start: function () {
        const $priceSlider = this.$('.tp-price-slider');
        $priceSlider.ionRangeSlider({
            skin: 'square',
            prettify_separator: ',',
            type: 'double',
            hide_from_to: true,
            onChange: ev => {
                this.$('input.min_price').val(ev.from);
                this.$('input.max_price').val(ev.to);
                this.$('.tp-price-validate').text('');
                this.$('.apply').removeClass('d-none');
            },
        });
        this.priceSlider = $priceSlider.data('ionRangeSlider');
        return this._super.apply(this, arguments);
    },
    _onChangePrice: function (ev) {
        ev.preventDefault();
        const minValue = this.$('input.min_price').val();
        const maxValue = this.$('input.max_price').val();

        if (isNaN(minValue) || isNaN(maxValue)) {
            this.$('.tp-price-validate').text(_t('Enter valid price value'));
            this.$('.apply').addClass('d-none');
            return false;
        }
        if (parseInt(minValue) > parseInt(maxValue)) {
            this.$('.tp-price-validate').text(_t('Max price should be greater than min price'));
            this.$('.apply').addClass('d-none');
            return false;
        }
        this.priceSlider.update({
            from: minValue,
            to: maxValue,
        });
        this.$('.tp-price-validate').text('');
        this.$('.apply').removeClass('d-none');
        return false;
    },
    _onClickApply: function (ev) {
        this.$('input[name=min_price]').remove();
        this.$('input[name=max_price]').remove();
        if (this.priceSlider.result.from !== this.priceSlider.result.min) {
            this.$el.append($('<input>', {type: 'hidden', name:'min_price', value: this.priceSlider.result.from}));
        }
        if (this.priceSlider.result.to !== this.priceSlider.result.max) {
            this.$el.append($('<input>', {type: 'hidden', name:'max_price', value: this.priceSlider.result.to}));
        }
    },
});

});
