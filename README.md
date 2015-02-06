# WebPlatform Notes server

Distribution of [Hypothes.is](http://hypothes.is/) annotator system.

First, edit the .ini files to add two settings to the ``[app:main]`` section,
``webplatform.client_id`` and ``webplatform.client_secret``. These are the
OAuth client credentials for the application.

Then, add settigs for ``api.key`` and ``api.secret``. The key can be anything
and will appear as the agent string in the consumer field of saved annotations.
The secret is used to sign API tokens.

Design document: http://docs.webplatform.org/wiki/WPD:Projects/SSO/Hypothesis

```shell
$ ./bootstrap
$ ./run
```

To use same environment as in production you can use `run` script in this way:

```shell
source bin/activate;./run --reload --paste production.ini --log-config production.ini
```

## Environment variables

Some configuration options are available in the following files and
are generally denoted in the code as `os.environ`.

* DATABASE_URL
* ELASTICSEARCH_INDEX
* ELASTICSEARCH_PORT
* ELASTICSEARCH_PORT_9200_TCP_ADDR
* ELASTICSEARCH_PORT_9200_TCP_PORT
* MAIL_PORT_25_TCP_ADDR
* MAIL_PORT_25_TCP_PORT
* REDIS_PORT_6379_TCP_ADDR
* REDIS_PORT_6379_TCP_PORT
* SESSION_SECRET
