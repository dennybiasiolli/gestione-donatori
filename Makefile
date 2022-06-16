style-fix:
	autoflake --in-place --remove-unused-variables --remove-all-unused-imports --ignore-init-module-imports --recursive .
	isort --profile black --line-length=79 .
	black --line-length=79 --skip-string-normalization .
	autopep8 --in-place --aggressive --recursive .
	flake8 --max-line-length=79 --max-doc-length=72 --ignore=E203,W503

style-check:
	pylint --load-plugins pylint_django --django-settings-module=website.settings_test --errors-only --recursive=y .
	autoflake --check --remove-unused-variables --remove-all-unused-imports --ignore-init-module-imports --recursive .
	isort --check-only --profile black --line-length=79 .
	black --check --diff --line-length=79 --skip-string-normalization .
	autopep8 --diff --exit-code --aggressive --recursive .
	flake8 --max-line-length=79 --max-doc-length=72 --ignore=E203,W503

test:
	python manage.py test --settings=website.settings_test --parallel=4

test-coverage:
	coverage run --concurrency=multiprocessing manage.py test --settings=website.settings_test --parallel=4
	coverage combine
	coverage report -m
	coverage html
	coverage xml
