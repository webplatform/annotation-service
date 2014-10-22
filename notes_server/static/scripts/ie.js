(function loader(d, t) {
  if ( typeof document.querySelectorAll !== 'undefined' ) {
    var s = document.querySelectorAll('link[type="application/annotator+html"]');

    if ( /Trident/.test(navigator.userAgent) === true && !!s.length ) {
      var appAttr = s[0].href;
      window.hypothesisConfig = function () {
        return {
          app: appAttr,
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
