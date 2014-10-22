var channel = Channel.build({
  origin: window.location.protocol + '//' + window.location.host,
  scope: 'notes:auth',
  window: window.opener,
  onReady: function () {
    channel.call({
      method: 'success',
      params: window.session,
      success: function () {
        window.close();
      }
    });
  }
});
