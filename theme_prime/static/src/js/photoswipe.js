odoo.define('theme_prime.photoswipe', function (require) {
'use strict';

var core = require('web.core');
var publicWidget = require('web.public.widget');

var _t = core._t;

publicWidget.registry.TpPhotoSwipe = publicWidget.Widget.extend({
    selector: '.tp-photoswipe-container',
    disabledInEditableMode: true,
    read_events: {
        'click .tp-photoswipe-img': '_onClickImage',
    },
    _onClickImage: function (ev) {
        this.items = _.map(this.$('.tp-photoswipe-box'), function (el) {
            const $img = $(el).find('.tp-photoswipe-img');
            if ($img.length) {
                return {
                    src: $img.attr('src'),
                    w: $img[0].naturalWidth,
                    h: $img[0].naturalHeight,
                    title: $img.attr('alt') || $img.attr('title'),
                };
            } else {
                return {
                    src: '/web/static/src/img/mimetypes/video.svg',
                    w: 300,
                    h: 300,
                    title: _t('Video'),
                };
            }
        });
        this.photoSwipe = new PhotoSwipe($('.pswp')[0], PhotoSwipeUI_Default, this.items, {
            shareButtons: [{id: 'download', label: _t('Download image'), url: '{{raw_image_url}}', download: true}],
            index: $(ev.currentTarget).parents('.tp-photoswipe-box').index(),
            closeOnScroll: false,
            bgOpacity: 0.8,
            tapToToggleControls: false,
            clickToCloseNonZoomable: false,
        });
        this.photoSwipe.init();
    },
});

});
