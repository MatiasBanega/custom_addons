odoo.define('theme_prime.notification.manger', function (require) {
"use strict";

var Notification = require('web.Notification');

return Notification.extend({
    template: "DroggolNotification",
    xmlDependencies: (Notification.prototype.xmlDependencies || []).concat(['/theme_prime/static/src/xml/core/notification_manager.xml']),

    /**
    * @override
    */
    init: function (parent, params) {
        this._super.apply(this, arguments);
        this.d_icon = params.d_icon;
        this.d_image = params.d_image;
    },
    start: function () {
        this.autohide = _.cancellableThrottleRemoveMeSoon(this.close, 5000, {leading: false});
        this.$el.on('shown.bs.toast', () => {
            this.autohide();
        });
        return this._super.apply(this, arguments);
    },
});
});
