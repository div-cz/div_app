$(document).ready(function() {
    document.emojiSource = '/static/tam-emoji/img';
    $('#summernote').summernote({
        lang: 'cs-CZ',
        placeholder: 'Můj příspěvek do blogu',
        tabsize: 2,
        height: 120,
        toolbar: [
            ['style', ['style']],
            ['font', ['bold', 'underline']],
            ['color', ['color']],
            ['para', ['ul', 'ol', 'paragraph']],
            ['table', ['table']],
            ['emoji', ['emoji']],
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