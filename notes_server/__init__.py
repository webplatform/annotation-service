# -*- coding: utf-8 -*-
import json

from annotator.auth import Consumer
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPFound
from pyramid.path import AssetResolver
from pyramid.security import remember
from pyramid.view import view_config
from requests_oauthlib import OAuth2Session
from requests import Request

from h.interfaces import IConsumerClass
from h.auth.local.views import session


AUTHZ_ENDPOINT = 'https://oauth.accounts.webplatform.org/v1/authorization'
TOKEN_ENDPOINT = 'https://oauth.accounts.webplatform.org/v1/token'
PROFILE_ENDPOINT = 'https://profile.accounts.webplatform.org/v1/session/read'


def consumer_factory(key, **kwargs):
    inst = Consumer(key)
    inst.__dict__.update(kwargs)
    return inst


@view_config(route_name='webplatform.login')
@view_config(route_name='webplatform.callback',
             renderer='notes_server:templates/oauth.pt')
def login(request):
    registry = request.registry
    settings = registry.settings
    session = request.session

    code = request.params.get('code')
    state = session.get('oauth_state')

    authz_endpoint = request.route_url('webplatform.authorize')
    token_endpoint = request.route_url('webplatform.token')

    wp_key = settings['webplatform.client_id']
    wp_secret = settings['webplatform.client_secret']

    provider = OAuth2Session(wp_key, scope=['session'], state=state)

    if code is not None:
        try:
            assert state == session['oauth_state']
            del session['oauth_state']
            req = Request('POST', token_endpoint,
                          data=json.dumps({
                              'client_id': wp_key,
                              'client_secret': wp_secret,
                              'code': code,
                          }))
            prepped = provider.prepare_request(req)
            provider.token = provider.send(prepped).json()
            provider._client.access_token = provider.token['access_token']
            profile = provider.get(PROFILE_ENDPOINT)
            provider_login = profile.json()['username']
            userid = 'acct:{}@{}'.format(provider_login, request.domain)
            request.response.headerlist.extend(remember(request, userid))
            return dict(result=profile.text)
        except Exception as e:
            pass

    location, state = provider.authorization_url(authz_endpoint)
    location = location.replace('response_type=code&', '')  # unused
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

    config.add_view(session, accept='application/json', name='app',
                    renderer='json')

    # XXX: https://github.com/sontek/pyramid_webassets/issues/53
    h_asset_path = AssetResolver().resolve('h:static').abspath()
    h_asset_url = 'assets/h'
    config.add_static_view(h_asset_url, 'h:static')
    config.add_webassets_path(h_asset_path, h_asset_url)

    config.override_asset('h:templates/blocks.pt',
                          'notes_server:templates/blocks.pt')

    config.scan(__name__)


def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include(includeme)
    return config.make_wsgi_app()
