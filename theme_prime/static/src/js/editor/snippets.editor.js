odoo.define('theme_prime.website.snippet.editor', function (require) {
'use strict';

const {_lt} = require('web.core');
const weSnippetEditor = require('web_editor.snippet.editor');
const options = require('web_editor.snippets.options');
const ThemeConfigDialog = require('theme_prime.core.theme_config.dialog');
require('website.snippet.editor');

const { _t } = require('web.core');

options.registry.PrimeTab = options.Class.extend({
    themePrimeConfigurations(previewMode, widgetValue, params) {
        new ThemeConfigDialog(this, {renderFooter: false, renderHeader: false, title: _t('Configurations')}).open();
    },
});

weSnippetEditor.Class.include({
    events: _.extend({}, weSnippetEditor.Class.prototype.events, {
        'click .o_we_customize_prime_btn': '_onPrimeTabClick',
    }),
    tabs: _.extend({}, weSnippetEditor.Class.prototype.tabs, {
        PRIME: 'prime',
    }),
    primeTabStructure: [
        ['theme-prime-customize', _lt("Customize")],
    ],
    _updateLeftPanelContent: function ({content, tab}) {
        this._super(...arguments);
        this.$('.o_we_customize_prime_btn').toggleClass('active', tab === this.tabs.PRIME);
    },
    async _onPrimeTabClick(ev) {
        // Note: nothing async here but start the loading effect asap
        this._execWithLoadingEffect(async () => new Promise(resolve => setTimeout(() => resolve(), 0)), false, 0);

        if (!this.topFakePrimeOptionEl) {
            let el;
            for (const [elementName, title] of this.primeTabStructure) {
                const newEl = document.createElement(elementName);
                newEl.dataset.name = title;
                if (el) {
                    el.appendChild(newEl);
                } else {
                    this.topFakePrimeOptionEl = newEl;
                }
                el = newEl;
            }
            this.bottomFakePrimeOptionEl = el;
            this.el.appendChild(this.topFakePrimeOptionEl);
        }

        // Need all of this in that order so that:
        // - the element is visible and can be enabled and the onFocus method is
        //   called each time.
        // - the element is hidden afterwards so it does not take space in the
        //   DOM, same as the overlay which may make a scrollbar appear.
        this.topFakePrimeOptionEl.classList.remove('d-none');
        const editor = await this._activateSnippet($(this.bottomFakePrimeOptionEl));
        this.topFakePrimeOptionEl.classList.add('d-none');
        editor.toggleOverlay(false);

        this._updateLeftPanelContent({
            tab: this.tabs.PRIME,
        });
    },
});

});
