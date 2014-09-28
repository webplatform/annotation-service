configure = ['$locationProvider', '$routeProvider', 'identityProvider',
  function  ( $locationProvider,   $routeProvider,   identityProvider ) {
    $locationProvider.html5Mode(true);

    $routeProvider.when('/wpd/callback', {
      resolve: {
        channel: ['$window', function ($window) {
          var _channel = Channel.build({
            origin: $window.location.origin,
            scope: 'annotator:auth',
            window: $window.opener,
            onReady: function () {
              _channel.call({
                method: 'success',
                params: $window.oauth_status,
                success: function () {
                  $window.close();
                }
              });
            }
          });
          return _channel;
        }],
      },
      redirectTo: '/viewer'
    });

    identityProvider.checkAuthorization = ['$q', function ($q) {
      return $q.when({userid: null});
    }]

    identityProvider.requestAuthorization = ['$q', function ($q) {
      return $q.when({userid: null});
    }]
  }
];


angular.module('h.auth', ['h.identity'], configure)
