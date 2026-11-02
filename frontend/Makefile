.PHONY: install dev build lint check preview

NPM ?= npm

install:
	$(NPM) ci

dev:
	$(NPM) run dev

build:
	$(NPM) run build

lint:
	$(NPM) run lint

check: lint build

preview:
	$(NPM) run preview
