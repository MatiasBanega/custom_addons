odoo.define('theme_prime.wysiwyg.widgets.media', function (require) {

const IconWidget = require('wysiwyg.widgets.media').IconWidget;

IconWidget.include({
    xmlDependencies: IconWidget.prototype.xmlDependencies.concat(
        ['/theme_prime/static/src/xml/icon-packs/wysiwyg.xml']
    ),
    save: function () {
        const iconFont = this._getFont(this.selectedIcon) || {base: 'fa', font: ''};
        if (iconFont.base === 'dri') {
            this.nonIconClasses = this.nonIconClasses.filter(icon => !_.contains(['fa'], icon));
        }
        if (iconFont.base === 'fa') {
            this.nonIconClasses = this.nonIconClasses.filter(icon => !_.contains(['dri'], icon));
        }
        return this._super.apply(this, arguments);
    },
});

});
