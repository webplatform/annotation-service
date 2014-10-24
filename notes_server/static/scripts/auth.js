configure = ['identityProvider', 'sessionProvider',
  function  ( identityProvider,   sessionProvider ) {
    var authCheck = null;

    identityProvider.checkAuthentication = [
      '$q', '$window', 'session', function ($q, $window, session) {
        authCheck = $q.defer();

        //$window.ssoOptions.onlogin = function () {
          session.load().$promise.then(
            function (data) {
              if (data.userid && data.csrf) {
                authCheck.resolve(data.csrf);
              } else {
                authCheck.reject('no session');
              }
            },
            function () {
              authCheck.reject('request failure');
            }
          );
        //};

        /*$window.ssoOptions.onlogout = function () {
          session.logout().$promise.then(function () {
            authCheck.reject('no session');
          });
        };

        $window.sso.init($window.ssoOptions);
        $window.sso.check();*/

        return authCheck.promise;
      }
    ];

    identityProvider.requestAuthentication = [
      '$q', '$window', function ($q, $window) {
        var authRequest = $q.defer();
        var left = Math.round(($window.screen.width - 720) / 4);
        var top = Math.round(($window.screen.height - 360) / 3);
        var dims = 'left=' + left + ',top=' + top;
        var props = 'dependent,dialog,width=320,height=460,' + dims;
        var popup = $window.open('/login', 'NotesAuth', props);
        var channel = Channel.build({
          origin: $window.location.protocol + '//' + $window.location.host,
          scope: 'notes:auth',
          window: popup
        }).bind('success', function (ctx, data) {
          if (data.userid && data.csrf) {
            authRequest.resolve(data.csrf);
          } else {
            authRequest.reject('canceled')
          }
          popup.close();
        });
        return authCheck.promise.catch(function () {
          return authRequest.promise;
        });
      }
    ];

    identityProvider.forgetAuthentication = [
      '$window', 'session', function ($window, session) {
        //$window.sso.signOut();
        return session.logout({}).$promise
      }
    ];

    sessionProvider.actions.load = {
      method: 'GET',
      withCredentials: true
    };

    sessionProvider.actions.logout = {
      method: 'POST',
      withCredentials: true,
      params: {
        __formid__: 'logout'
      }
    };
  }
];


angular.module('h.auth', ['h.identity', 'h.session'], configure)
