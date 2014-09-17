from pyramid.authentication import RemoteUserAuthenticationPolicy


class WebPlatformAuthenticationPolicy(RemoteUserAuthenticationPolicy):
    def unauthenticated_userid(self, request):
        return None
    

def includeme(config):
    config.include('pyramid_oauthlib')
    config.set_authentication_policy(WebPlatformAuthenticationPolicy())

