release: pip install -r requirements_deploy.txt
release: python manage.py migrate

web: gunicorn website.wsgi
