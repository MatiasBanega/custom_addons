odoo.define('theme_prime.widgets.ui_configurator_widget', function (require) {
'use strict';

const {_t, qweb} = require('web.core');
const AbstractWidget = require('theme_prime.widgets.abstract_widget');
const CardRegistry = require('theme_prime.card_registry');
const DialogWidgetRegistry = require('theme_prime.dialog_widgets_registry');

let UIConfiguratorWidget = AbstractWidget.extend({

    template: 'd_ui_configurator_widget',

    xmlDependencies: AbstractWidget.prototype.xmlDependencies.concat(['/theme_prime/static/src/xml/editor/widgets/ui_configurator_widget.xml', '/theme_prime/static/src/xml/cards.xml']),

    events: _.extend({}, AbstractWidget.prototype.events, {
        'click .d_configurator_option:not(.d_disabled)': '_onConfigOptionClick',
        'click .d_layout_btn': '_onDisplayBtnClick',
        'change .d-select-card-style': '_onChangeStyle',
    }),

    d_tab_info: {icon: 'fa fa-cogs', label: _t('UI Configurator'), name: 'UIConfiguratorWidget'},
    d_attr: 'data-user-params',

    /**
     * @override
     * @returns {Promise}
     */
    willStart: function () {
        let defs = [this._super.apply(this, arguments)];
        defs.push(this._fetchShopConfig().then(data => {
            this.shopConfigParams = data;
            this._setOptionData();
        }));
        return Promise.all(defs);
    },
    /**
    * @override
    * @returns {Promise}
    */
    start: function () {
        this._initTips();
        this.demo_data = this._getDemodata();
        this._refreshPreview();
        return this._super.apply(this, arguments);
    },
    /**
     * @override
     * @returns {Array} Selected configuration parameters
     */
    WidgetCurrentstate: function () {
        this.userParams['ppr'] = parseInt(this.$('#num_of_products').val());
        this.userParams['layoutType'] = this.$('.d_layout_btn.d_active').attr('data-option');
        this.userParams['snippetStyle'] = this.$('.d-select-card-style').val();
        let {ppr, layoutType} = this.userParams;
        if (layoutType === 'grid') {
            this.userParams['col_size'] = parseInt(12 / ppr);
        }
        return {
            d_attr: this.d_attr,
            value: this.userParams
        };
    },
    /**
     * @override
     */
    setWidgetState: function (options) {
        this.snippetStyle = _.has(options, 'snippetStyle') ? options.snippetStyle : 's_card_style_1';
        this._setSnippetParams(this.snippetStyle, false);
        this.shopConfigParams = {};
        this.allSnippets = CardRegistry.keys();
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * fetch shop configuration data if there is no products
     *
     * @private
     */
    _fetchShopConfig: function () {
        return this._rpc({
            route: '/theme_prime/get_shop_config'
        });
    },
    /**
     * @private
     */
    _getAllActions: function () {
        return ['wishlist', 'comparison', 'add_to_cart', 'quick_view'];
    },
    /**
     * Je options hoy ae options related info label icon ane name.
     *
     * @private
     * @returns {Object} Returns options related data.
     */
    _getCardOptionsInfo: function () {
        return {
            quick_view: {icon: 'dri dri-eye', label: _t('QUICK VIEW'), name: 'quick_view'},
            add_to_cart: {icon: 'dri dri-cart', label: _t('ADD TO CART'), name: 'add_to_cart'},
            category_info: {icon: 'fa fa-font', label: _t('CATEGORY'), name: 'category_info'},
            wishlist: {icon: 'fa fa-heart-o', label: _t('WISHLIST'), name: 'wishlist'},
            comparison: {icon: 'dri dri-compare', label: _t('COMPARE'), name: 'comparison'},
            rating: {icon: 'fa fa-star', label: _t('RATING'), name: 'rating'},
            description_sale: {icon: 'fa fa-align-left', label: _t('DESCRIPTION'), name: 'description_sale'},
            label: {icon: 'fa fa-tag', label: _t('LABEL'), name: 'label'},
            images: {icon: 'fa fa-photo', label: _t('MULTI-IMAGES'), name: 'images'},
            show_similar: { icon: 'fa fa-clone', label: _t('SIMILAR'), name: 'show_similar'}
        };
    },
    /**
     * options ni default values
     *
     * @private
     * @returns {Object} Returns default option.
     */
    _getDefaultOptions: function () {
        return { quick_view: true, add_to_cart: true, wishlist: true, comparison: true, description_sale: false, rating: true, label: true, ppr: 4, col_size: 12 / 4, images: false, layoutType: 'slider', category_info: false, show_similar:false};
    },
    /**
     * product na data default values
     *
     * @private
     * @returns {Object} Returns demo data.
     */
    _getDemodata: function () {
        return {
            website_url: '#',
            img_medium: '/theme_prime/static/src/img/s_config_data.png',
            name: 'Product Name',
            price: '$ 13.00',
            rating: qweb.render('rating_demo_tmpl'),
            label: 'Label',
            lable_color: 'blue',
            label_style: '1',
            has_discounted_price: true,
            description_sale: 'This is short product description.',
            list_price: '$ 22.10',
            category_info: {
                name: 'Category Name',
                id: 1,
            },
            // to-do handel images
            images: [],
        };
    },
    /**
     * Je options hoy ae options related info label icon ane name.
     *
     * @private
     * @returns {Object} Returns options related data.
     */
    _getlayoutOptionsInfo: function () {
        return {grid: {icon: 'fa fa-th', label: _t('GRID'), name: 'grid', selector: 'd_layout_btn'}, slider: {icon: 'fa fa-arrows-h', label: _t('SLIDER'), name: 'slider', selector: 'd_layout_btn'}};
    },
    /**
     * Returns Array of options that must be disabled for configurator
     * if option is Disabled from shop configuration.
     * e.g: if rating is disabled that means the rating feature is not available
     * for the shop.
     *
     * But feature like add to cart, description can be used by snippet
     * even if it is disabled from shop.
     *
     * @private
     * @returns {Array} Returns Array.
     */
    _getMustDisabledOptions: function () {
        return ['wishlist', 'comparison', 'rating'];
    },
    /**
     * init tooltips
     *
     * @private
     */
    _initTips: function () {
        this.$('[data-toggle="tooltip"]').tooltip();
    },
    /**
     * @private
     */
    _isanyActionEnabled: function () {
        return _.contains(_.values(_.pick(this.userParams, this._getAllActions())), true);
    },
    /**
     * Refresh preview
     *
     * @private
     */
    _refreshPreview: function () {
        this.$('.d_snippet_previewer').empty().append(qweb.render('ui_configurator_preview', {widget: this}));
    },
    /**
     * Refresh preview
     *
     * @private
     */
    _refreshLeftPanel: function () {
        let tmpl = qweb.render('d_snippet_options_panel', {widget: this});
        this.$('.d_left_panel').empty().append(tmpl);
    },
    /**
     * Refresh preview
     *
     * @private
     */
    _refreshWidget: function () {
        this._setSnippetParams(this.snippetStyle, true);
        this._setOptionData();
        this._refreshLeftPanel();
        this._refreshPreview();
        this._initTips();
    },
    /**
     * Set card parameters e.g add_to_cart etc.
     *
     * @private
     */
    _setCardOptions: function () {
        let self = this;
        let optionsInfo = this._getCardOptionsInfo();
        this.cardOptions = [];
        let shopConfigParams = this.shopConfigParams;
        let mustDisabledOptions = this._getMustDisabledOptions();
        _.each(this.snippetParams, function (val, key) {
            let option = optionsInfo[key];
            if (val && option) {
                option['selector'] = 'd_configurator_option';
                // shopConfigParams
                let enabledInShop = shopConfigParams['is_' + key + '_active'];
                // if disabled in shop config and must need to disabled for configurator.
                if (_.contains(mustDisabledOptions, key) && !enabledInShop) {
                    // show it disabled
                    option['is_disabled'] = true;
                    // don't show active
                    option['active'] = false;
                    option['title'] = _.str.sprintf(_t('This snippet supports %s feature but it is disabled form <b>Shop</b> configuration.'), key);
                    // userParams to false so get correct preview
                    self.userParams[key] = false;
                } else {
                    option['is_disabled'] = false;
                    option['active'] = self.userParams[key];
                }
                // enabled form shop or not
                self.cardOptions.push(option);
            }
        });
    },
    /**
     * Set display parameters e.g grid or slider.
     *
     * @private
     */
    _setLayoutOptions: function () {
        let self = this;
        this.layoutOptions = [];
        let layoutType = this.userParams.layoutType;
        let options = this._getlayoutOptionsInfo();
        _.each(options, function (option) {
            option['active'] = false;
            if (layoutType === option.name) {
                option['active'] = true;
            }
            self.layoutOptions.push(option);
        });
    },
    /**
     * icon ane label ni values fill karava mate.
     * aa method ae option active che k nai ae value pan add karse
     *
     * @private
     */
    _setOptionData: function () {
        this._setCardOptions();
        this._setLayoutOptions();
        this.userParams['anyActionEnabled'] = this._isanyActionEnabled();
    },
    /**
     * Use user config value by default
     * If the data is not provided by user then it will be decided by the system.
     *
     * @private
     * @param {String} snippet name
     * @param {Boolean} useDefalutVals
     */
    _setSnippetParams: function (snippet, useDefalutVals) {
        let SnippetConfig = CardRegistry.get(snippet);
        // default values of the fields
        let defaults = this._getDefaultOptions();
        // feature support by snippet
        this.snippetParams = _.defaults(_.pick(SnippetConfig.options || {}, _.keys(defaults)), defaults);
        this.parentClass = SnippetConfig.parentClass;
        this.previewTemplate = SnippetConfig.previewTemplate;
        if (useDefalutVals) {
            this.userParams = this.snippetParams;
            this.userParams.snippetStyle = snippet;
        } else {
            this.userParams = this.options || this.snippetParams;
        }
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
    * @private
    * @param {Event} ev
    */
    _onChangeStyle: function (ev) {
        this.snippetStyle = $(ev.currentTarget).val();
        this._refreshWidget();
    },
    /**
     * @private
     * @param {Event} ev
     */
    _onConfigOptionClick: function (ev) {
        let $target = $(ev.currentTarget);
        $target.toggleClass('d_active');
        this.userParams[$target.attr('data-option')] = $target.hasClass('d_active');
        this.userParams['anyActionEnabled'] = this._isanyActionEnabled();
        this._refreshPreview();
    },
    /**
     * @private
     * @param {Event} ev
     */
    _onDisplayBtnClick: function (ev) {
        this.$('.d_layout_btn').removeClass('d_active');
        $(ev.currentTarget).addClass('d_active');
    },
});

DialogWidgetRegistry.add('UIConfiguratorWidget', UIConfiguratorWidget);

return UIConfiguratorWidget;
});
