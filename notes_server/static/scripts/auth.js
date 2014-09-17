configure = ['$routeProvider',
  function  ( $routeProvider ) {
    $routeProvider.when('/wpd/callback', {
      resolve: {
        channel: ['$window', function ($window) {
          var _channel = Channel.build({
            origin: $window.location.origin,
            scope: 'annotator:auth',
            window: $window.opener,
            onReady: function () {
              _channel.call(
                method: 'success',
                params: $window.oauth_status,
                success: function () {
                  $window.close();
                }
              });
            });
          });
          return _channel;
        ]
      },
      redirectTo: '/viewer'
    });
];


angular.module('webplatform.notesServer', [], configure)
