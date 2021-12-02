odoo.define('theme_prime.frontend', function (require) {
'use strict';

require('web.dom_ready');
const config = require('web.config');
const isMobileEnv = config.device.size_class <= config.device.SIZES.LG && config.device.touch;

// Enable bootstrap tooltip
$('[data-toggle="tooltip"]').tooltip({
    delay: {show: 100, hide: 100},
});

if (!isMobileEnv) {
    var $backToTopButton = $('.tp-back-to-top');
    $('#wrapwrap').scroll(function() {
        ($(this).scrollTop() > 800) ? $backToTopButton.fadeIn(400) : $backToTopButton.fadeOut(400);
    });
    $backToTopButton.click(function(ev) {
        ev.preventDefault();
        $('html, body').animate({ scrollTop: 0 });
    });
}

});
