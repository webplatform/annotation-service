SHELL := bash
PATH := bin:${PATH}
NODE_MODULES := ./node_modules/coffee-script/bin


default:

		@yes | ./bootstrap


deps:

		@gem install sass compass compass-flexbox
		@npm install coffee-script


local:

		export COFFEE_BIN="node_modules/coffee-script/bin/coffee"
		test -f localdev.pem || openssl genrsa -out localdev.pem
		test -f localdev.crt || openssl req -new -x509 -key localdev.pem -out localdev.crt -days 1024 -subj "/C=US/ST=MA/L=Cambridge/O=W3C/OU=WebPlatform/CN=localhost"
		bin/gunicorn --reload --paste development.ini --log-config development.ini --certfile=localdev.crt --keyfile=localdev.pem

clean:

		find . -type f -name '*.pyc'


.PHONY: default
