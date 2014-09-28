configure = ['identityProvider',
  function  ( identityProvider ) {
    identityProvider.checkAuthorization = [
      '$q', function ($q) {
        return $q.when({userid: null});
      }
    ];

    identityProvider.requestAuthorization = [
      '$q', '$window', function ($q, $window) {
        var deferred = $q.defer();
        var left = Math.round(($window.screen.width - 720) / 4);
        var top = Math.round(($window.screen.height - 360) / 3);
        var dims = 'left=' + left + ',top=' + top;
        var props = 'dependent,dialog,width=320,height=460,' + dims;
        var popup = $window.open('/wpd/login', 'NotesAuth', props);
        var channel = Channel.build({
          origin: $window.location.origin,
          scope: 'notes:auth',
          window: popup
        }).bind('success', function (ctx, data) {
          deferred.resolve(data);
          popup.close();
        });
        return deferred.promise;
      }
    ];

    identityProvider.forgetAuthorization = [
      '$q', function ($q) {
        return $q.when({userid: null});
      }
    ];
  }
];


angular.module('h.auth', ['h.identity'], configure)
