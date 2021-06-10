#!/bin/sh

#if [ -n "$DJANGO_SUPERUSER_USERNAME"] && [ -n "$DJANGO_SUPERUSER_PASSWORD"]; then
#    (cd /app/captiveportal; python manage.py createsuperuser --no-input)
#fi

set -e # exit on errors

cd /app/captiveportal


# If the settings file is missing, do initial setup
if [ ! -f "/data/settings" ]; then
    # First run, generate random secret_key
    export SECRET_KEY=$(dd if=/dev/urandom bs=60 count=1 2>/dev/null | base64 | head -n 1)
    echo "SECRET_KEY=\"$SECRET_KEY\"" > /data/settings
fi

# Import environment variables from settings file
set -a
. /data/settings
set +a

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py createcachetable

if [ "$SUPERUSER_USERNAME" ]; then
    export DJANGO_SUPERUSER_PASSWORD=$SUPERUSER_PASSWORD
    python manage.py createsuperuser --no-input --username "$SUPERUSER_USERNAME" --email "$SUPERUSER_EMAIL" || echo "Could not create superuser."
fi

gunicorn captiveportal.wsgi -b 0.0.0.0:8000 --workers 3 &

nginx 
