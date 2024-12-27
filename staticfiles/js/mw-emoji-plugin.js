(function ($) {
    $.extend($.summernote.plugins, {
        'customEmoji': function (context) {
            var self = this;
            var ui = $.summernote.ui;
            var emojis = {
                ':smile:': '😊',
                ':laughing:': '😆',
                ':blush:': '😊',
                ':heart_eyes:': '😍',
                ':wink:': '😉',
                ':cry:': '😢',
                ':angry:': '😠',
                ':sunglasses:': '😎',
                ':thumbsup:': '👍',
                ':thumbsdown:': '👎'
            };

            self.initialize = function () {
                // Create the emoji panel
                self.$panel = $('<div class="custom-emoji-menu"></div>').hide();
                var $items = $('<div class="custom-emoji-items"></div>');
                
                // Append emoji items
                $.each(emojis, function (key, value) {
                    var $item = $('<a href="javascript:void(0)" title="' + key + '">' + value + '</a>');
                    $item.on('click', function () {
                        context.invoke('editor.insertText', key);
                        self.$panel.hide();
                    });
                    $items.append($item);
                });

                self.$panel.append($items);
                self.$panel.appendTo('body');

                // Hide panel on clicking outside
                $(document).on('click.customEmoji', function (e) {
                    if (!self.$panel.is(e.target) && self.$panel.has(e.target).length === 0) {
                        self.$panel.hide();
                    }
                });
            };

            context.memo('button.customEmoji', function () {
                var button = ui.button({
                    contents: '<i class="fa fa-smile-o"></i>',
                    click: function () {
                        if (!self.$panel) {
                            self.initialize();
                        }
                        // Toggle panel visibility
                        self.$panel.toggle();
                    }
                });
                return button.render();
            });
        }
    });
})(jQuery);
