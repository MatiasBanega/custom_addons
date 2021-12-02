odoo.define('droggol_theme_common.list_view_brand', function (require) {
"use strict";

const core = require('web.core');
const Dialog = require('web.Dialog');
const ListController = require('web.ListController');
const ListView = require('web.ListView');
const viewRegistry = require('web.view_registry');

const _t = core._t;

const BrandListController = ListController.extend({
    buttons_template: 'BrandListView.buttons',
    events: _.extend({}, ListController.prototype.events, {
        'click .o_button_reorder': '_onClickReorder',
    }),
    _onClickReorder: function () {
        const self = this;
        Dialog.confirm(this, _t('This will reorder sequence of all brands based on alphabetical order (from A to Z).'), {
            confirm_callback: function () {
                self._rpc({
                    model: self.modelName,
                    method: 'reorder_sequence',
                }).then(() => self.reload());
            }
        });
    },
});

const BrandListView = ListView.extend({
    config: _.extend({}, ListView.prototype.config, {
        Controller: BrandListController,
    }),
});

viewRegistry.add('dr_list_view_brand', BrandListView);

});
