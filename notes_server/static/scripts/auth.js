configure = ['identityProvider',
  function  ( identityProvider ) {
    identityProvider.checkAuthentication = [
      '$q', function ($q) {
        return $q.reject('session restore not implemented')
      }
    ];

    identityProvider.requestAuthentication = [
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
          if (data.userid && data.csrf) {
            deferred.resolve(data.csrf);
          } else {
            deferred.reject('canceled')
          }
          popup.close();
        });
        return deferred.promise;
      }
    ];

    identityProvider.forgetAuthentication = [
      '$q', function ($q) {
        return $q.when({userid: null});
      }
    ];
  }
];


angular.module('h.auth', ['h.identity'], configure)
