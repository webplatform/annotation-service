(function () {
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
  }
})();
