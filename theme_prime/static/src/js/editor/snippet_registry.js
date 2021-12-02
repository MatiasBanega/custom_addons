odoo.define('theme_prime.card_registry', function (require) {
"use strict";

var Registry = require('web.Registry');

return new Registry();

});

odoo.define('theme_prime._card_registry', function (require) {
"use strict";

var cardRegistry = require('theme_prime.card_registry');

cardRegistry
    .add('s_card_style_1', {previewTemplate: 's_card_style_1', parentClass: 's_card_style_1'})
    .add('s_card_style_2', {previewTemplate: 's_card_style_2', parentClass: 's_card_style_2'})
    .add('s_card_style_3', {previewTemplate: 's_card_style_3', parentClass: 's_card_style_3', options: { category_info: true, show_similar:true}})
    .add('s_card_style_4', {previewTemplate: 's_card_style_4', parentClass: 's_card_style_4', options: {category_info: true, description_sale: true, quick_view: false}})
    .add('s_card_style_5', {previewTemplate: 's_card_style_5', parentClass: 's_card_style_5', options: {images: true, category_info: true}})
    .add('s_card_style_6', {previewTemplate: 's_card_style_6', parentClass: 's_card_style_6', options: {show_similar: true}})
    .add('s_card_style_7', {previewTemplate: 's_card_style_7', parentClass: 's_card_style_7'});

});

odoo.define('theme_prime.category_filter_registry', function (require) {
"use strict";

var Registry = require('web.Registry');

return new Registry();

});

odoo.define('theme_prime._category_filter_registry', function (require) {
"use strict";

var categoryFilterRegistry = require('theme_prime.category_filter_registry');

categoryFilterRegistry
    .add('d_category_filter_style_1', {filterTemplate: 'd_category_filter_style_1'})
    .add('d_category_filter_style_2', {filterTemplate: 'd_category_filter_style_2'})
    .add('d_category_filter_style_3', {filterTemplate: 'd_category_filter_style_3'})
    .add('d_category_filter_style_4', {filterTemplate: 'd_category_filter_style_4'})
    .add('d_category_filter_style_5', {filterTemplate: 'd_category_filter_style_5'})
    .add('d_category_filter_style_6', {filterTemplate: 'd_category_filter_style_6'});

});

odoo.define('theme_prime.collection_style_registry', function (require) {
"use strict";

var Registry = require('web.Registry');

return new Registry();

});

odoo.define('theme_prime._collection_style_registry', function (require) {
"use strict";

var CollectionStyleRegistry = require('theme_prime.collection_style_registry');

CollectionStyleRegistry
    .add('d_card_collection_style_1')
    .add('d_card_collection_style_2')
    .add('d_card_collection_style_3');

});

odoo.define('theme_prime.hierarchical_category_styles', function (require) {
"use strict";

var Registry = require('web.Registry');

return new Registry();

});

odoo.define('theme_prime._hierarchical_category_styles', function (require) {
"use strict";

var hierarchicalCategoryStyleRegistry = require('theme_prime.hierarchical_category_styles');

hierarchicalCategoryStyleRegistry
    .add('s_tp_hierarchical_category_style_1')
    .add('s_tp_hierarchical_category_style_2')
    .add('s_tp_hierarchical_category_style_3');

});
odoo.define('theme_prime.category_ui_card_widget_styles', function (require) {
"use strict";

var Registry = require('web.Registry');

return new Registry();

});

odoo.define('theme_prime._category_ui_card_widget_styles', function (require) {
"use strict";

var categoryUICardWidget = require('theme_prime.category_ui_card_widget_styles');

categoryUICardWidget
    .add('s_tp_category_style_1')
    .add('s_tp_category_style_2')
    .add('s_tp_category_style_3')
    .add('s_tp_category_style_4')
    .add('s_tp_category_style_5');

});

odoo.define('theme_prime.dialog_widgets_registry', function (require) {
"use strict";

var Registry = require('web.Registry');

return new Registry();

});

odoo.define('theme_prime.snippet_registry', function (require) {
"use strict";

var Registry = require('web.Registry');

return new Registry();

});

odoo.define('theme_prime._snippet_registry', function (require) {
"use strict";

var snippetRegistry = require('theme_prime.snippet_registry');

snippetRegistry
    .add('d_products_snippet', {widgets: ['ProductsWidget', 'UIConfiguratorWidget']})
    .add('d_category_snippet', {widgets: ['CategoryWidget', 'UIConfiguratorWidget', 'CategoryUIWidget']})
    .add('d_single_category_snippet', {widgets: ['CategoryWidget'], defaultValue: {select2Limit: 1}})
    .add('d_single_product_snippet', {widgets: ['ProductsWidget'], defaultValue: {select2Limit: 1, noSwicher: true}})
    .add('s_d_single_product_cover_snippet', {widgets: ['ProductsWidget'], defaultValue: {select2Limit: 1, noSwicher: true}})
    .add('d_products_collection', {widgets: ['CollectionWidget', 'CollectionUIWidget']})
    .add('d_top_categories', {widgets: ['CategoryWidget'], defaultValue: {select2Limit: 3}})
    .add('d_custom_collection', {widgets: ['CollectionWidget', 'UIConfiguratorWidget', 'CategoryUIWidget']})
    .add('s_d_product_count_down', {widgets: ['ProductsWidget']})
    .add('s_d_product_small_block', {widgets: ['ProductsWidget']})
    .add('s_d_single_product_count_down', {widgets: ['ProductsWidget']})
    .add('s_d_image_products_block', {widgets: ['ProductsWidget']})
    .add('s_d_products_grid', {widgets: ['ProductsWidget'], defaultValue: {select2Limit: 9, noSwicher: true}})
    .add('s_tp_hierarchical_category_snippet', {widgets: ['HierarchicalCategories', 'hierarchicalCategoryUIWidget']})
    .add('s_category_snippet', {widgets: ['HierarchicalCategories', 'categoryUiCardWidget'], defaultValue: {noChild: true}});

});
