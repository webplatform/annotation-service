# -*- coding: utf-8 -*-
import json
import datetime

from annotator.auth import Consumer
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPFound
from pyramid.session import signed_serialize, signed_deserialize
from pyramid.view import view_config
from requests_oauthlib import OAuth2Session
from requests import Request

from h.api import get_consumer
from h.interfaces import IConsumerClass


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

    now = datetime.datetime.utcnow()
    client = get_consumer(request)
    code = request.params.get('code')
    state = request.params.get('state')

    authz_endpoint = request.route_url('webplatform.authorize')
    token_endpoint = request.route_url('webplatform.token')

    wp_key = settings['webplatform.client_id']
    wp_secret = settings['webplatform.client_secret']

    expected = signed_serialize(now, 'webplatform.' + client.secret)
    provider = OAuth2Session(wp_key, scope=['session'], state=expected)

    if code is not None:
        try:
            then = signed_deserialize(state, 'webplatform.' + client.secret)
            assert (then - now).total_seconds() <= 300
            req = Request('POST', token_endpoint,
                          data=json.dumps({
                              'client_id': wp_key,
                              'client_secret': wp_secret,
                              'code': code,
                          }))
            prepped = provider.prepare_request(req)
            provider.token = provider.send(prepped).json()
            provider._client.access_token = provider.token['access_token']
            return provider.get(PROFILE_ENDPOINT).json()
        except:
            pass

    location, _ = provider.authorization_url(authz_endpoint)
    location = location.replace('response_type=code&', '')  # unused
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
