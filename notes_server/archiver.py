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


def entry(request, annotation):
    quote = '> ' + ('\n\n> '.join(quotes(annotation)))
    username = annotation.get('user').split('@')[0].split(':', 1)[1]
    env = {'annotation': annotation, 'quote': quote, 'username': username}
    template = 'notes_server:templates/archive.txt'
    return render(template, env, request=request)


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
    subject = "[note] {}".format(title).strip()
    body = entry(request, annotation).decode('utf-8')
    # TODO: use config mail.default_sender value here
    sender = "notifier-notes@webplatform.org"

    message = Message(sender=sender, recipients=recipients,
                      subject=subject, body=body)

    get_mailer(request).send(message)


def includeme(config):
    config.scan(__name__)
