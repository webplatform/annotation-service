(function loader(d, t) {
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

    var g = d.createElement(t),
        s = d.getElementsByTagName(t)[0];
        g.src = 'https://notes.webplatform.org/embed.js';
        s.parentNode.insertBefore(g, s);
  }
}(document, 'script'));
