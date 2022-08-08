[![flake8 Lint](https://github.com/csae8092/my-arche-gui/actions/workflows/lint.yml/badge.svg)](https://github.com/csae8092/my-arche-gui/actions/workflows/lint.yml)

# My ARCHE GUI

A django/python based read-only-gui based upon the ARCHE-API. The purpose of this repo is mainly to get acquainted to ARCHE's API.

## install

* clone the repo
* change into the project's root directory e.g. `cd my-arche-gui`
* create a virtual environment e.g. `virutalenv env` and activate it `source env/bin/activate`
* install required packages `pip install -r requirements_dev.txt`
* go to [http://127.0.0.1:8000](http://127.0.0.1:8000/) and check if everything works


## Docker

`./build_and_run.sh`

### building the image

* `docker build -t myagui:latest .`
* `docker build -t myagui:latest --no-cache .`


### running the image

To run the image you should provide an `.env` file to pass in needed environment variables; see example below:

* `docker run -it -p 8020:8020 --rm --env-file env.default --name myagui myagui:latest`

-----

This project was bootstraped by [djangobase-cookiecutter](https://github.com/acdh-oeaw/djangobase-cookiecutter)