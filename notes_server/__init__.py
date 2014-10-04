# -*- coding: utf-8 -*-
import json

from annotator.auth import DEFAULT_TTL, Consumer
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPFound
from pyramid.path import AssetResolver
from pyramid.security import remember
from pyramid.view import view_config
from pyramid_layout.layout import layout_config
from requests_oauthlib import OAuth2Session
from requests import Request

from h.auth.local.views import model
from h.layouts import BaseLayout, AppLayout as BaseAppLayout
from h.interfaces import IConsumerClass

import logging
log = logging.getLogger(__name__)


AUTHZ_ENDPOINT = 'https://oauth.accounts.webplatform.org/v1/authorization'
TOKEN_ENDPOINT = 'https://oauth.accounts.webplatform.org/v1/token'
SESSION_ENDPOINT = 'https://profile.accounts.webplatform.org/v1/session/'


class OAuthConsumer(Consumer):
    def __init__(self, key, **kwargs):
        super(OAuthConsumer, self).__init__(key)
        kwargs.setdefault('ttl', DEFAULT_TTL)
        self.__dict__.update(kwargs)

    @property
    def client_id(self):
        return unicode(self.key)

    @property
    def client_secret(self):
        return unicode(self.secret)


@layout_config(name='app', template='notes_server:templates/base.pt')
class AppLayout(BaseAppLayout):
    pass


@layout_config(name='auth', template='h:templates/base.pt')
class AuthLayout(BaseLayout):
    app = None
    requirements = (('jschannel', None), ('webplatform-callback', None))


@view_config(layout='auth',
             renderer='notes_server:templates/auth.pt',
             route_name='login')
@view_config(layout='auth',
             renderer='notes_server:templates/auth.pt',
             route_name='callback')
def login(request):
    registry = request.registry
    settings = registry.settings
    session = request.session

    code = request.params.get('code')
    state = request.params.get('state')

    authz_endpoint = request.route_url('authorize')
    token_endpoint = request.route_url('token')

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
            profile = provider.get(SESSION_ENDPOINT + 'read')
            provider_login = profile.json()['username']
            userid = 'acct:{}@{}'.format(provider_login, request.domain)
            request.response.headerlist.extend(remember(request, userid))
            return dict(session=json.dumps(model(request)))
        except Exception:
            log.exception('error processing oauth callback')

    location, state = provider.authorization_url(authz_endpoint)
    location = location.replace('response_type=code&', '')  # unused
    session['oauth_state'] = state
    return HTTPFound(location=location)


@view_config(renderer='json', route_name='recover')
def recover_session(request):
    #payload = request.params.get('recoveryPayload')
    #req = Request('POST', SESSION_ENDPOINT + 'recover',
    #              headers={'Authorization': payload})
    #r = req.send()
    return {}


def includeme(config):
    registry = config.registry
    settings = registry.settings

    registry.registerUtility(OAuthConsumer, IConsumerClass)
    config.include('h')

    authz_endpoint = settings.get('webplatform.authorize', AUTHZ_ENDPOINT)
    config.add_route('authorize', authz_endpoint)

    token_endpoint = settings.get('webplatform.token', TOKEN_ENDPOINT)
    config.add_route('token', token_endpoint)

    config.add_route('login', '/wpd/login')
    config.add_route('callback', '/wpd/callback')
    config.add_route('recover', '/wpd/recover')

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
