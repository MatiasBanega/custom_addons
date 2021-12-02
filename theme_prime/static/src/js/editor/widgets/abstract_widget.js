odoo.define('theme_prime.widgets.abstract_widget', function (require) {
'use strict';

var Widget = require('web.Widget');

return Widget.extend({

    xmlDependencies: [],
    /**
     * @constructor
     * @param {Object} options: useful parameters such as productIDs, domain etc.
     */
    init: function (parent, options) {
        this._super.apply(this, arguments);
        this.options = options;
        this.setWidgetState(options);
    },

    //--------------------------------------------------------------------------
    // Getters
    //--------------------------------------------------------------------------

    /**
     * @returns {string}
     */
    WidgetCurrentstate: function () {
        return {};
    },

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     *
     * Set default values.
     *
     * @abstract
     */
    setWidgetState: function (options) {},
});

});
