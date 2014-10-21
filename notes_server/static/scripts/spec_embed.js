(function () {
  if ( typeof document.querySelectorAll !== 'undefined' ) {
    var selector = document.querySelectorAll('link[type="application/annotator+html"]');

    if ( /Trident\//.test(navigator.userAgent) === false ) {
      window.hypothesisConfig = function () {
        return {
          app: selector.attr('href'),
          Heatmap: {container: '.annotator-frame'},
          Toolbar: {container: '.annotator-frame'},
          DomTextMapper: {skip: true}
        };
      };
    }

  var tag = document.createElement('script'),
      embedUrl = 'https://notes.webplatform.org/embed.js';

  tag.setAttribute('src', embedUrl);
  document.body.appendChild(tag);
})();
