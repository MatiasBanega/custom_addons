odoo.define('theme_prime.wysiwyg_multizone', function (require) {
'use strict';

var WysiwygMultizone = require('web_editor.wysiwyg.multizone');
var snippetsEditor = require('web_editor.snippet.editor');

WysiwygMultizone.include({
    start: function () {
        return this._super.apply(this, arguments).then(() => {
            if (this.$('.tp-shop-offer-zone').length) {
                this.editor.snippetsMenu.toggleOfferSnippets(true);
            }
            if (this.$('#category_header').length) {
                this.editor.snippetsMenu.toggleCategorySnippets(true);
            }
        });
    },
});

snippetsEditor.Class.include({
    /**
     * @private
     * @param {boolean} show
     */
    toggleOfferSnippets: function (show) {
        setTimeout(() => this._activateSnippet(false));
        this._showShopOfferSnippets = show;
        this._filterSnippets();
    },
    /**
     * @private
     * @param {boolean} show
     */
    toggleCategorySnippets: function (show) {
        setTimeout(() => this._activateSnippet(false));
        this._showShopCategorySnippets = show;
        this._filterSnippets();
    },
    /**
     * @override
     */
    _filterSnippets(search) {
        this._super(...arguments);
        if (!this._showShopOfferSnippets) {
            this.el.querySelector('#tp_snippet_shop_offer').classList.add('d-none');
        }
        if (!this._showShopCategorySnippets) {
            this.el.querySelector('#tp_snippet_shop_category').classList.add('d-none');
        }
    },
});

});
