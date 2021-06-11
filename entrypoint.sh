#!/bin/sh

set -e # exit on errors

cd /app

# If there is no SECRET_KEY, and the settings file is missing, do initial setup
if [ -z "${SECRET_KEY}" ]; then
    echo "SECRET_KEY not specified in environment, checking /data/settings"

    if [ ! -f "/data/settings" ]; then
        echo "Generating new SECRET_KEY and saving to /data/settings"
        # First run, generate random secret_key
        export SECRET_KEY=$(dd if=/dev/urandom bs=60 count=1 2>/dev/null | base64 | head -n 1)
        echo "SECRET_KEY=\"$SECRET_KEY\"" > /data/settings
    fi

    echo "Loading SECRET_KEY from /data/settings"
    # Import environment variables from settings file
    set -a
    . /data/settings
    set +a
fi

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py createcachetable

if [ "$SUPERUSER_USERNAME" ]; then
    export DJANGO_SUPERUSER_PASSWORD=$SUPERUSER_PASSWORD
    python manage.py createsuperuser --no-input --username "$SUPERUSER_USERNAME" --email "$SUPERUSER_EMAIL" || echo "Could not create superuser."
fi

gunicorn captiveportal.wsgi -b 0.0.0.0:8000 --workers 3 &

nginx 
