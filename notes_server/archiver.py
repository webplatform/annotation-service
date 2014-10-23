# -*- coding: utf-8 -*-
import re
import logging
from urlparse import urlparse

from requests import RequestException, get
from bs4 import BeautifulSoup
from pyramid.events import subscriber
from pyramid.renderers import render
from pyramid.security import Everyone, principals_allowed_by_permission
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

from h import events

log = logging.getLogger(__name__)  # pylint: disable=invalid-name

ARCHIVE_TEMPLATE = 'notes_server:templates/archive.txt'


def quotes(annotation):
    result = []
    for target in annotation.get('target', []):
        for selector in target.get('selector', []):
            if 'exact' in selector:
                result.append(selector['exact'])
    return result


# TODO: Memoize if troublesome, or offload caching to a proxy
def reply_to(uri):
    r = get(uri)
    parsed = BeautifulSoup(r.text)
    anchors = parsed.select('a[rel="reply-to"]')
    return [
        anchor['href'][7:]
        for anchor in anchors
        if re.match(r'^mailto:', anchor['href'], re.IGNORECASE)
    ]


def valid_recipients(unvalidated, uri):
    url_struct = urlparse(uri)
    domain = re.sub(r'^(www.)?', '', url_struct.hostname)
    domain_re = '@{}$'.format(re.escape(domain))
    return [
        email
        for email in unvalidated
        if re.search(domain_re, email) is not None
    ]


@subscriber(events.AnnotationEvent)
def notification(event):
    annotation = event.annotation
    request = event.request

    # Send only creations
    if event.action != 'create':
        return

    # Send only for public annotations
    if Everyone not in principals_allowed_by_permission(annotation, 'read'):
        return

    uri = annotation['uri']

    try:
        mail_links = reply_to(uri)
    except RequestException:
        log.info('Archiver could not fetch source document at %s', uri)
        return

    recipients = valid_recipients(mail_links, uri)
    if len(recipients) == 0:
        return

    title = annotation.get('document', {}).get('title', '')

    try:
        user = re.match(r'acct:([^@]+)', annotation['user']).group(1)
    except (AttributeError, KeyError):
        log.info('Archiver could not parse user "%s"', annotation.get('user'))

    env = dict(annotation=annotation, quotes=quotes, title=title, user=user)

    subject = "[note] {}".format(title).strip()
    body = render(ARCHIVE_TEMPLATE, env, request=request).decode('utf-8')
    message = Message(recipients=recipients, subject=subject, body=body)

    get_mailer(request).send(message)
