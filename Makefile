SRC_DIR=$(shell pwd)
NPM:=npm --prefix $(SRC_DIR)/rc_car/frontend

deps:
	$(NPM) update
	pip install -r requirements.txt

build:
	mkdir -p $(SRC_DIR)/rc_car/frontend
	cd $(SRC_DIR)/rc_car/frontend && $(shell ${NPM} bin)/elm-make \
		app/Main.elm --output=js/index.js

dev-server: build
	python -m rc_car

deploy:
	rm -rf dist
	python setup.py sdist
	scp ./dist/rc-car-0.1.tar.gz pi@192.168.100.6:~/rc-car-0.1.tar.gz

lint:
	flake8 \
		--ignore=E731,C812,C815 --max-line-length=120 \
		--import-order-style=pep8 \
		--application-package-names=rc_car \
		./rc_car
