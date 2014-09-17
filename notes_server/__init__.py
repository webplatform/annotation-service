# -*- coding: utf-8 -*-
def includeme(config):
    config.include('notes_server.auth')
    config.override_asset('h:templates/', 'notes_server:templates/')
