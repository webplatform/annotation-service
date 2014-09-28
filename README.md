# WebPlatform Notes server

Distribution of [Hypothes.is](http://hypothes.is/) annotator system.

First, edit the .ini files to add two settings to the ``[app:main]`` section,
``webplatform.client_id`` and ``webplatform.client_secret``. These are the
OAuth client credentials for the application.

Then, add settigs for ``api.key`` and ``api.secret``. The key can be anything
and will appear as the agent string in the consumer field of saved annotations.
The secret is used to sign API tokens.

```shell
$ ./bootstrap
$ ./run
```
