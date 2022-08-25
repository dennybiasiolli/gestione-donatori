style-fix:
	isort .
	black .
	flake8

style-check:
	pylint --load-plugins pylint_django --django-settings-module=website.settings_test --errors-only --recursive=y .
	isort --check-only .
	black --check --diff .
	flake8

test:
	python manage.py test --settings=website.settings_test --parallel=4

test-coverage:
	coverage run --concurrency=multiprocessing manage.py test --settings=website.settings_test --parallel=4
	coverage combine
	coverage report -m
	coverage html
	coverage xml
