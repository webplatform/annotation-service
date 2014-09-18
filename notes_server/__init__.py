# -*- coding: utf-8 -*-
import json

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from requests_oauthlib import OAuth2Session
from requests import Request

AUTHZ_ENDPOINT = 'https://oauth.accounts.webplatform.org/v1/authorization'
TOKEN_ENDPOINT = 'https://oauth.accounts.webplatform.org/v1/token'
PROFILE_ENDPOINT = 'https://profile.accounts.webplatform.org/v1/session/read'


@view_config(route_name='webplatform.login')
@view_config(route_name='webplatform.callback', renderer='h:templates/oauth.pt')
def login(request):
    registry = request.registry
    settings = registry.settings
    session = request.session

    key = settings['webplatform.client_id']
    secret = settings['webplatform.client_secret']
    code = request.params.get('code')
    state = session.get('oauth_state')
    scope = ['session']
    provider = OAuth2Session(key, scope=scope, state=state)

    authz_endpoint = request.route_url('webplatform.authorize')
    token_endpoint = request.route_url('webplatform.token')
    profile_endpoint = 'https://profile.accounts.webplatform.org/v1/session/read'

    if code is not None:
        try:
            assert request.params['state'] == session['oauth_state']
            req = Request('POST', token_endpoint,
                          data=json.dumps({
                              'client_id': key,
                              'client_secret': secret,
                              'code': code,
                          }))
            prepped = provider.prepare_request(req)
            provider.token = provider.send(prepped).json()
            provider._client.access_token = provider.token['access_token']
            result = provider.get(profile_endpoint)
            return dict(result=json.dumps(result))
        except:
            pass

    location, state = provider.authorization_url(authz_endpoint)
    location = location.replace('response_type=code&', '')
    session['oauth_state'] = state
    return HTTPFound(location=location)


def includeme(config):
    registry = config.registry
    settings = registry.settings

    registry.registerUtility(consumer_factory, IConsumerClass)
    config.include('h')

    authz_endpoint = settings.get('webplatform.authorize', AUTHZ_ENDPOINT)
    config.add_route('webplatform.authorize', authz_endpoint)

    token_endpoint = settings.get('webplatform.token', TOKEN_ENDPOINT)
    config.add_route('webplatform.token', token_endpoint)

    config.add_route('webplatform.login', '/wpd/login')
    config.add_route('webplatform.callback', '/wpd/callback')
    config.scan(__name__)


def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include(includeme)
    return config.make_wsgi_app()
