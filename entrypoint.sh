#!/bin/sh

set -e # exit on errors

cd /app

# Local configuration is stored in /data/local_settings.py, and imported by settings.py
# By default the only important setting it will contain is SECRET_KEY, but additional advanced
# settings can be configured or overridden there.
if [ ! -f "/data/local_settings.py" ]; then
    echo "Generating /data/local_settings.py"
    SECRET_KEY=$(dd if=/dev/urandom bs=60 count=1 2>/dev/null | base64 | head -n 1)
    cp local_settings.template /data/local_settings.py
    sed -i "s|^SECRET_KEY .*\$|SECRET_KEY = \"${SECRET_KEY}\"|" /data/local_settings.py
fi

if [ ! -f "/data/local_urls.py" ]; then
    echo "Creating initial /data/local_urls.py file"
    cp local_urls.template /data/local_urls.py
fi

# Link local files to the appropriate places inside the app directory
ln -s /data/local_settings.py /app/captiveportal/local_settings.py || true
ln -s /data/local_urls.py /app/captiveportal/local_urls.py || true

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py createcachetable

if [ "$SUPERUSER_USERNAME" ]; then
    export DJANGO_SUPERUSER_PASSWORD=$SUPERUSER_PASSWORD
    python manage.py createsuperuser --no-input --username "$SUPERUSER_USERNAME" --email "$SUPERUSER_EMAIL" || echo "Could not create superuser."
fi

gunicorn captiveportal.wsgi -b 0.0.0.0:8000 --workers 3 &

nginx 
