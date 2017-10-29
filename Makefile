SRC_DIR=$(shell pwd)
NPM:=npm --prefix $(SRC_DIR)/rc_car/frontend
RASPBERRY_HOST:=192.168.100.1

deps:
	$(NPM) update
	pip install -r requirements.txt

build:
	mkdir -p $(SRC_DIR)/rc_car/frontend
	cd $(SRC_DIR)/rc_car/frontend && $(shell ${NPM} bin)/elm-make \
		app/Main.elm --output=js/index.js

run: build
	mkdir -p data
	python -m rc_car --config ${SRC_DIR}/conf/rc_car.ini

deploy:
	rm -rf dist
	python setup.py sdist
	scp ./dist/rc-car-0.1.tar.gz pi@${RASPBERRY_HOST}:~/rc-car-0.1.tar.gz

lint:
	flake8 \
		--ignore=E731,C812,C815 --max-line-length=120 \
		--import-order-style=pep8 \
		--application-package-names=rc_car \
		./rc_car
