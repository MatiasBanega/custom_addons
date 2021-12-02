odoo.define('theme_prime.core.theme_config.dialog', function (require) {
'use strict';

    var Dialog = require('web.Dialog');
    var Widget = require('web.Widget');
    const {_t, qweb} = require('web.core');

    var AbstractThemeOption = Widget.extend({
        key: false,
        option_template: false,
        init: function (parent, options) {
            this.options = _.defaults(options || {}, {imageURL: false});
            this.value = odoo.dr_theme_config[this.key];
            this.dirty = false;
            this._super.apply(this, arguments);
        },
        start: function () {
            return this._super.apply(this, arguments).then(() => {
                return this._render();
            });
        },

        /**
         * This method will be called from outside to.
         */
        getExportValue: function () {
            return this.value;
        },

        /**
         * This method is used to set internal state and render widget again.
         */
        setValue: function (value) {
            this.value = value;
            this.dirty = true;
            this._render();
        },
        getValue: function () {
            return this.value;
        },

        _render: function (value) {
            var $option = qweb.render(this.option_template, {value: this.value, image: this.getImageURL, widget: this});
            this.$el.children().remove();
            return this.$el.append($option);
        },

        getImageURL: function () {
            return this.imageURL;
        },
    });

    var ThemeOptionCartFlow = AbstractThemeOption.extend({
        option_template: 'theme_config.CartFlow',
        key: 'cart_flow',
        selection_options: [['default', 'Default'], ['notification', 'Notification'], ['dialog', 'Dialog'], ['side_cart', 'Open Cart Sidebar']],
        events: {change: '_onChange'},
        _onChange: function (ev) {
            this.setValue(this.$("input[name='cart_flow']:checked").val());
        }
    });

    var ThemeOptionGeneralCategorySearch = AbstractThemeOption.extend({
        option_template: 'theme_config.GeneralCategorySearch',
        key: 'bool_general_show_category_search',
        events: {change: '_onChange'},
        _onChange: function (ev) {
            this.setValue(this.$('#general_show_category_search').prop('checked'));
        }
    });

    var ThemeOptionGeneralLanguagePricelistSelector = AbstractThemeOption.extend({
        option_template: 'theme_config.GeneralLanguagePricelistSelector',
        key: 'json_general_language_pricelist_selector',
        events: {change: '_onChange'},
        _onChange: function (ev) {
            var vals = { hide_country_flag: this.$('#general_hide_country_flag').prop('checked') };
            this.setValue(vals);
        }
    });

    var ThemeOptionBottomBarOnScroll = AbstractThemeOption.extend({
        option_template: 'theme_config.BottomBarOnScroll',
        key: 'bool_show_bottom_bar_onscroll',
        events: {change: '_onChange'},
        _onChange: function (ev) {
            this.setValue(this.$('.tp-enable-bottombar-on-scroll').prop('checked'));
        }
    });
    var ThemeOptionBottomBar = AbstractThemeOption.extend({
        option_template: 'theme_config.BottomBar',
        key: 'bool_display_bottom_bar',
        events: {change: '_onChange'},
        _onChange: function (ev) {
            this.setValue(this.$('.tp-enable-bottombar').prop('checked'));
        }
    });

    var ThemeOptionMobileSortFilters = AbstractThemeOption.extend({
        option_template: 'theme_config.MobileSortFilters',
        key: 'bool_mobile_filters',
        events: {change: '_onChange'},
        _onChange: function (ev) {
            this.setValue(this.$('.tp-enable-mobile-filter').prop('checked'));
        }
    });

    var ThemeOptionGeneralBrandsPage = AbstractThemeOption.extend({
        option_template: 'theme_config.GeneralBrandsPage',
        key: 'json_brands_page',
        events: {change: '_onChange'},
        _onChange: function (ev) {
            var vals = { disable_brands_grouping: this.$('#general_disable_brands_grouping').prop('checked') };
            this.setValue(vals);
        }
    });

    var ThemeOptionZoom = AbstractThemeOption.extend({
        option_template: 'theme_config.Zoom',
        key: 'json_zoom',
        events: { change: '_onChange' },
        _onChange: function (ev) {
            var vals = { zoom_enabled: this.$('#zoom_enabled').prop('checked'), disable_small: this.$('#disable_small').prop('checked'), zoom_factor: parseInt(this.$('#zoom_factor').val()) || 2 };
            this.setValue(vals);
        }
    });
    var ThemeOptionAjaxLoadProducts = AbstractThemeOption.extend({
        option_template: 'theme_config.ajaxLoadProducts',
        key: 'bool_enable_ajax_load',
        events: {change: '_onChange'},
        _onChange: function (ev) {
            this.setValue(this.$('.tp-enable-ajax-load').prop('checked'));
        }
    });
    var ThemeOptionBottombarConfig = AbstractThemeOption.extend({
        option_template: 'theme_config.BottombarConfig',
        key: 'json_bottom_bar_config',
        events: {change: '_onChange'},
        /**
         *
         * @override
         */
        willStart: function () {
            return this._super.apply(this, arguments).then(() => Promise.all([this._fetchData()]));
        },
        _render: function () {
            this._super.apply(this, arguments);
            this.$select2input = this.$('.tp-select2-input');
            this.$select2input.select2({maximumSelectionSize: 8});
        },
        _fetchData: function () {
            return this._rpc({
                model: 'website',
                method: 'get_theme_prime_bottom_bar_action_buttons',
            }).then((data) => {
                this.data = data;
            });
        },
        _onChange: function (ev) {
            this.setValue(this.$select2input.val());
        }
    });

    var ThemeOptionCategoryPills = AbstractThemeOption.extend({
        option_template: 'theme_config.CategoryPills',
        key: 'json_category_pills',
        events: {change: '_onChange'},
        _onChange: function (ev) {
            var vals = { enable: this.$('#category_pills_enabled').prop('checked'), enable_child: this.$('#category_pills_enabled_child').prop('checked'), hide_desktop: this.$('#category_pills_hide_desktop').prop('checked'), show_title: this.$('#category_pills_show_title').prop('checked'), style: parseInt(this.$('#category_pills_style').val())};
            this.setValue(vals);
        }
    });

    var ThemeOptionGridProduct = AbstractThemeOption.extend({
        option_template: 'theme_config.GridProduct',
        key: 'json_grid_product',
        events: { change: '_onChange' },
        _onChange: function (ev) {
            var vals = {
                show_color_preview: this.$('#grid_product_color_preview').prop('checked'),
                show_quick_view: this.$('#grid_product_quick_view').prop('checked'),
                show_similar_products: this.$('#grid_product_similar_products').prop('checked'),
                show_rating: this.$('#grid_product_rating').prop('checked')
            };
            this.setValue(vals);
        }
    });

    var ThemeOptionShopFilters = AbstractThemeOption.extend({
        option_template: 'theme_config.ShopFilters',
        key: 'json_shop_filters',
        events: { change: '_onChange' },
        _onChange: function (ev) {
            var vals = {
                in_sidebar: this.$('#shop_filters_in_sidebar').prop('checked'),
                collapsible: this.$('#shop_filters_collapsible').prop('checked'),
                show_category_count: this.$('#shop_filters_show_category_count').prop('checked'),
                show_attrib_count: this.$('#shop_filters_show_attrib_count').prop('checked'),
                hide_attrib_value: this.$('#shop_filters_hide_attrib_value').prop('checked'),
                show_price_range_filter: this.$('#show_price_range_filter').prop('checked'),
                price_range_display_type: this.$('#price_range_display_type').val(),
                show_rating_filter: this.$('#shop_filters_show_rating').prop('checked'),
                show_brand_search: this.$('#shop_filters_show_brand_search').prop('checked'),
                show_labels_search: this.$('#shop_filters_show_labels_search').prop('checked'),
                show_tags_search: this.$('#shop_filters_show_tags_search').prop('checked'),
                brands_style: parseInt(this.$('#brands_style').val()),
                tags_style: parseInt(this.$('#tags_style').val()),
            };
            this.setValue(vals);
        }
    });

    var ThemeOptionStickyAddtoCart = AbstractThemeOption.extend({
        option_template: 'theme_config.StickyAddtoCart',
        key: 'bool_sticky_add_to_cart',
        events: { change: '_onChange' },
        _onChange: function (ev) {
            this.setValue(this.$('#sticky_add_to_cart_enabled').prop('checked'));
        }
    });

    var ThemeOptionProductOffers = AbstractThemeOption.extend({
        option_template: 'theme_config.ProductOffers',
        key: 'bool_product_offers',
        events: { change: '_onChange' },
        _onChange: function (ev) {
            this.setValue(this.$('#dr_product_dialog_offers').prop('checked'));
        }
    });

    var ThemeConfigDialog = Dialog.extend({
        template: 'theme_config.dialog',
        xmlDependencies: Dialog.prototype.xmlDependencies.concat(['/theme_prime/static/src/xml/editor/dialogs/snippet_configurator_dialog.xml', '/theme_prime/static/src/xml/core/theme_config.xml']),
        events: _.extend({}, Dialog.prototype.events || {}, {
            'click .tp-save-btn': '_onSaveDialog',
            'click .tp-close-btn': 'close',
        }),
        init: function (parent, options) {
            this.tabs = this._tabInfo();
            this.allWidgets = [];
            return this._super(parent, _.extend(options || {}, {
                title: options.title,
                size: options.size || 'extra-large',
                technical: false,
                dialogClass: 'd-snippet-config-dialog p-0'
            }));
        },

        start: function () {
            // Resolve conflict with configurator dialog
            this.$el.css('height', '100%');
            this.$('.dr-config-right').addClass('p-4');
            return this._super.apply(this, arguments).then(() => {
                return this.fillTabs();
            });
        },

        _tabInfo: function () {
            return [{
                name: 'GeneralConfig',
                icon: 'fa fa-sliders',
                label: _t('General'),
                widgets: [ThemeOptionCartFlow, ThemeOptionGeneralCategorySearch, ThemeOptionGeneralBrandsPage, ThemeOptionGeneralLanguagePricelistSelector]
            }, {
                name: 'ShopConfig',
                icon: 'fa fa-shopping-cart',
                label: _t('Shop'),
                widgets: [ThemeOptionGridProduct, ThemeOptionShopFilters, ThemeOptionCategoryPills, ThemeOptionAjaxLoadProducts]
            }, {
                name: 'ProductDetailConfig',
                icon: 'fa fa-cube',
                label: _t('Product Detail'),
                widgets: [ThemeOptionZoom, ThemeOptionStickyAddtoCart, ThemeOptionProductOffers]
            }, {
                name: 'MobileConfig',
                icon: 'fa fa-mobile',
                label: _t('Mobile'),
                widgets: [ThemeOptionBottombarConfig, ThemeOptionBottomBarOnScroll, ThemeOptionMobileSortFilters, ThemeOptionBottomBar]
            }];
        },

        fillTabs: function () {
            return _.map(this.tabs, tab => {
                var widgetObjs = _.map(tab.widgets, wid => new wid(this));
                this.allWidgets.push(...widgetObjs);
                var promises = _.map(widgetObjs, obj => obj.appendTo(this.$('#' + tab.name)));
                return Promise.all(promises);
            });
        },

        _onSaveDialog: function () {
            var payload = {};
            _.each(this.allWidgets, wid => {
                if (wid.dirty) {
                    payload[wid.key] = wid.getValue();
                }
            });
            return this._rpc({
                route: '/theme_prime/save_website_config',
                params: {
                    configs: payload,
                }
            }).then(() => window.location.reload());
        }
    });

    return ThemeConfigDialog;
});

odoo.define('theme_prime.core.theme_config', function (require) {
'use strict';

require('website.customizeMenu');
var ThemeConfigDialog = require('theme_prime.core.theme_config.dialog');
var websiteNavbarData = require('website.navbar');
const { _t, qweb } = require('web.core');


var ThemePrimeConfig = websiteNavbarData.WebsiteNavbarActionWidget.extend({
    actions: _.extend({}, websiteNavbarData.WebsiteNavbarActionWidget.prototype.actions || {}, {
        'open-theme-prime-config-dialog': '_openThemeConfigDialog',
    }),

    //--------------------------------------------------------------------------
    // Actions
    //--------------------------------------------------------------------------

    /**
     * Opens the Theme configurator dialog.
     *
     * @private
     */
    _openThemeConfigDialog: function () {
        new ThemeConfigDialog(this, {renderFooter: false, renderHeader: false, title: _t('Configurations')}).open();
    },
});

websiteNavbarData.websiteNavbarRegistry.add(ThemePrimeConfig, '#tp_prime_config');

return {
    ThemePrimeConfig: ThemePrimeConfig,
};
});
