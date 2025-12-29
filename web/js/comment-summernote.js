$(document).ready(function() {
    document.emojiSource = '/static/tam-emoji/img';
    $('#summernote').summernote({
        lang: 'cs-CZ',
        placeholder: 'Můj příspěvek',
        tabsize: 2,
        height: 120,
        toolbar: [
            ['font', ['bold', 'underline']],

            // ['color', ['color']],
            ['insert', ['link']],
            ['emoji', ['emoji']], // ensure correct toolbar options
        ],
        callbacks: {
            onPaste: function(e) {
            var bufferText = ((e.originalEvent || e).clipboardData || window.clipboardData).getData('Text');
            e.preventDefault();
            setTimeout(function () {
            document.execCommand('insertText', false, bufferText);
            }, 10);
            }
        }
    });
});