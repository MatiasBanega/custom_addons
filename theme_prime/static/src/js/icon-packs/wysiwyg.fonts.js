odoo.define('theme_prime.wysiwyg.fonts', function (require) {
'use strict';

const fonts = require('wysiwyg.fonts');

fonts.fontIcons.unshift({base: 'dri', parser: /\.(dri-(?:\w|-)+)::?before/i});

});
