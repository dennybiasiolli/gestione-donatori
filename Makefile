BOOTSTRAP_VERSION=5.3.2
BOOTSTRAP_ICON_VERSION=1.11.1

requirements:
	uv sync --locked --all-extras --dev

style-fix:
	uv run isort .
	uv run black .
	uv run flake8

style-check:
	uv run isort --check-only .
	uv run black --check --diff .
	uv run flake8

tests:
	uv run pytest
	uv run coverage html
	uv run coverage xml

get-static-libs:
	mkdir -p avis/static/libs

	rm -rf avis/static/libs/bootstrap
	mkdir -p avis/static/libs/bootstrap
	curl -o avis/static/libs/bootstrap/bootstrap.min.css \
		https://cdn.jsdelivr.net/npm/bootstrap@$(BOOTSTRAP_VERSION)/dist/css/bootstrap.min.css
	curl -o avis/static/libs/bootstrap/bootstrap.min.css.map \
		https://cdn.jsdelivr.net/npm/bootstrap@$(BOOTSTRAP_VERSION)/dist/css/bootstrap.min.css.map
	curl -o avis/static/libs/bootstrap/bootstrap.bundle.min.js \
		https://cdn.jsdelivr.net/npm/bootstrap@$(BOOTSTRAP_VERSION)/dist/js/bootstrap.bundle.min.js
	curl -o avis/static/libs/bootstrap/bootstrap.bundle.min.js.map \
		https://cdn.jsdelivr.net/npm/bootstrap@$(BOOTSTRAP_VERSION)/dist/js/bootstrap.bundle.min.js.map

	rm -rf avis/static/libs/bootstrap-icons
	mkdir -p avis/static/libs/bootstrap-icons
	curl -o avis/static/libs/bootstrap-icons/bootstrap-icons.css \
		https://cdn.jsdelivr.net/npm/bootstrap-icons@$(BOOTSTRAP_ICON_VERSION)/font/bootstrap-icons.css

	curl -Lo avis/static/libs/bootstrap-icons/bootstrap-icons.zip \
		https://github.com/twbs/icons/releases/download/v$(BOOTSTRAP_ICON_VERSION)/bootstrap-icons-$(BOOTSTRAP_ICON_VERSION).zip
	unzip avis/static/libs/bootstrap-icons/bootstrap-icons.zip -d avis/static/libs/bootstrap-icons
	mv avis/static/libs/bootstrap-icons/bootstrap-icons-$(BOOTSTRAP_ICON_VERSION)/fonts avis/static/libs/bootstrap-icons/fonts
	rm -r avis/static/libs/bootstrap-icons/bootstrap-icons-$(BOOTSTRAP_ICON_VERSION)
	rm avis/static/libs/bootstrap-icons/bootstrap-icons.zip
