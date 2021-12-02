odoo.define('theme_prime.specialMenu', function (require) {
"use strict";

require('website.content.menu');
var contentMenu = require('website.contentMenu');
let publicWidget = require('web.public.widget');

contentMenu.EditMenuDialog.include({
    xmlDependencies: contentMenu.EditMenuDialog.prototype.xmlDependencies.concat(
        ['/theme_prime/static/src/xml/special_menu.xml']
    ),
    events: _.extend({}, contentMenu.EditMenuDialog.prototype.events, {
        'click span.dr_special_menu': '_onClickSpecialMenu',
    }),
    _onClickSpecialMenu: function (ev) {
        var $menu = $(ev.currentTarget).closest('[data-menu-id]');
        var menuID = $menu.data('menu-id');
        var menu = this.flat[menuID];
        var isActive = menu.fields['dr_is_special_menu'];
        if (!isActive) {
            menu.fields['dr_is_special_menu'] = true;
            $menu.find('.dr_special_menu').addClass('badge-info');
        } else {
            menu.fields['dr_is_special_menu'] = false;
            $menu.find('.dr_special_menu').removeClass('badge-info');
        }
    },
});

publicWidget.registry.hoverableDropdown.include({
    _onMouseEnter: function (ev) {
        if ($(ev.currentTarget).hasClass('tp-disable-open-on-hover')) {
            return;
        }
        this._super.apply(this, arguments);
    },
    _onMouseLeave: function (ev) {
        if ($(ev.currentTarget).hasClass('tp-disable-open-on-hover')) {
            return;
        }
        this._super.apply(this, arguments);
    },
});

});
