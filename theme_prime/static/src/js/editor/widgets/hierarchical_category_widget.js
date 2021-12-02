odoo.define('theme_prime.widgets.hierarchical_category_widget', function (require) {
'use strict';

const AbstractWidget = require('theme_prime.widgets.abstract_widget');
const Select2Dialog = require('theme_prime.dialog.product_selector');
const DialogWidgetRegistry = require('theme_prime.dialog_widgets_registry');
const {SortableMixins, DroggolUtils, CategoryWidgetMixins} = require('theme_prime.mixins');

const {qweb, _t} = require('web.core');

let HierarchicalCategories = AbstractWidget.extend(SortableMixins, DroggolUtils, CategoryWidgetMixins, {
    template: 'theme_prime.hierarchical_category_widget',
    xmlDependencies: AbstractWidget.prototype.xmlDependencies.concat(['/theme_prime/static/src/xml/editor/widgets/hierarchical_category_widget.xml']),

    events: _.extend({}, AbstractWidget.prototype.events, {
        'click .d_add_category': '_onAddCategoryClick',
        'click .dr_add_child_category': '_onAddChildCategoryClick',
        'click .d_remove_item': '_onRemoveCategoryClick',
    }),
    d_tab_info: {icon: 'fa fa-list', label: _t('Category'), name: 'HierarchicalCategories'},
    d_attr: 'data-hierarchical-category-params',
    /**
     * @constructor
     * @param {Object} options: useful parameters such as categoryIDs
     */
    init: function (parent, options) {
        this._super.apply(this, arguments);
        this.categories = options.categories || [];
        this.noChild = options.noChild || false;
        let parentCategoryIDs = _.map(this.categories, function (data) {
            return data.id;
        });
        this.parentCategoryIDs = _.compact(parentCategoryIDs);
    },
    /**
     * @override
     */
    willStart: function () {
        let defs = [this._super.apply(this, arguments)];
        let self = this;
        if (this.parentCategoryIDs.length) {
            defs.push(this._fetchCategories(this.parentCategoryIDs).then(categoriesFromDB => {
                let FetchedCategories = _.map(categoriesFromDB, function (category) {
                    return category.id;
                });
                let categories = [];
                let parentCategoryIDs = [];
                _.each(this.parentCategoryIDs, function (parentCategoryID) {
                    if (_.contains(FetchedCategories, parentCategoryID)) {
                        let category = _.findWhere(self.categories, {id: parentCategoryID});
                        _.extend(category, _.findWhere(categoriesFromDB, {id: parentCategoryID}));
                        categories.push(category);
                        parentCategoryIDs.push(parentCategoryID);
                    }
                });
                this.categories = categories;
                this.parentCategoryIDs = parentCategoryIDs;
            }));
        }
        return Promise.all(defs);
    },
    /**
     * @override
     */
    start: function () {
        this._makeListSortable();
        this._togglePlaceHolder();
        return this._super.apply(this, arguments);
    },
    /**
     * @override
     * @returns {Array} list of selected products
     */
    WidgetCurrentstate: function () {
        let categories = _.map(this.$('.d_category_item'), function (category) {
            let $category = $(category);
            return {id: parseInt($category.attr('data-category-id'), 10), child: JSON.parse($category.attr('data-child'))};
        });
        return {d_attr: this.d_attr, value: {categories: _.compact(categories)}};
    },
    _togglePlaceHolder: function () {
        let items = this.$('.d_category_item').length;
        this.trigger_up('widget_value_changed', {val: items});
        this.$('.d-category-placeholder').toggleClass('d-none', !!items);
        this.$('.d_category_input_group').toggleClass('d-none', !items);
    },
    /**
     * @private
     */
    _refreshCategoryList: function () {
        let $categoryList = this.$('.d_sortable_block');
        $categoryList.empty();
        if (this.categories.length) {
            $categoryList.append(qweb.render('d_categories_list', {categories: this.categories, widget: this}));
        }
        this._togglePlaceHolder();
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onAddCategoryClick: function () {
        let self = this;
        this.CategoryDialog = new Select2Dialog(this, {
            multiSelect: true,
            records: this.categories,
            recordsIDs: this._getCategoryIDs(),
            routePath: '/theme_prime/get_category_by_name',
            fieldLabel: _t("Select Category"),
            dropdownTemplate: 'category_select2_dropdown',
        });
        this.CategoryDialog.on('d_product_pick', this, function (ev) {
            let categoriesToAdd = ev.data.result;
            if (categoriesToAdd) {
                let categoriesToFetch = _.difference(categoriesToAdd, self._getCategoryIDs());
                // already Fetch krelo data use karvo navi selected category ni info fetch kri che
                self._fetchCategories(categoriesToFetch).then(categories => {
                    _.each(categories, function (category) {
                        category['child'] = [];
                    });
                    let allCategories = _.union(categories, self.categories);
                    self.categories = _.map(categoriesToAdd, function (category) {
                        return _.findWhere(allCategories, {id: category});
                    });
                    self._refreshCategoryList();
                    self.parentCategoryIDs = self._getCategoryIDs();
                });
            } else {
                self.categories = [];
                self.parentCategoryIDs = [];
                this._refreshCategoryList();
            }
        });
        this.CategoryDialog.open();
    },
    _onAddChildCategoryClick: function (ev) {
        let $category = $(ev.currentTarget).closest('.d_category_item');
        let categoryID = parseInt($category.attr('data-category-id'), 10);
        let childCategories = JSON.parse($category.attr('data-child'));
        this._fetchCategories(childCategories).then(categories => {
            let CategoryDialog = new Select2Dialog(this, {
                multiSelect: true,
                records: categories,
                recordsIDs: childCategories,
                routePath: '/theme_prime/get_category_by_name',
                fieldLabel: _t("Select Category"),
                dropdownTemplate: 'category_select2_dropdown',
                routeParams: {
                    category_id: parseInt($category.attr('data-category-id'), 10)
                }
            });
            CategoryDialog.on('d_product_pick', this, function (ev) {
                let selectedChildCategory = ev.data.result;
                let category = _.findWhere(this.categories, {id: categoryID});
                category.child = selectedChildCategory;
                this._refreshCategoryList();
            });
            CategoryDialog.open();
        });
    },
    /**
     * @private
     * @param {Event} ev
     */
    _onRemoveCategoryClick: function (ev) {
        let $category = $(ev.currentTarget).closest('.d_category_item');
        $category.remove();
        this.categories = _.without(this.categories, _.findWhere(this.categories, {id: parseInt($category.attr('data-category-id'), 10)}));
        this.categoryIDs = this._getCategoryIDs();
        this._togglePlaceHolder();
    },
});


DialogWidgetRegistry.add('HierarchicalCategories', HierarchicalCategories);

return HierarchicalCategories;
});
