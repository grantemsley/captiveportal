FROM python:slim AS compile-image

RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential libldap2-dev libsasl2-dev libssl-dev gcc

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" 
COPY ./requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt



FROM python:slim as build-image

COPY --from=compile-image /opt/venv /opt/venv

EXPOSE 8080
STOPSIGNAL SIGTERM

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends nginx && rm -rf /var/lib/apt/lists/*

COPY nginx.default /etc/nginx/nginx.conf
RUN chown -R nobody:nogroup /var/lib/nginx && chown -R nobody:nogroup /var/log/nginx

COPY entrypoint.sh captiveportal local_settings.template local_urls.template ./
RUN chown -R nobody:nogroup /app

RUN mkdir /data && chown nobody:nogroup /data

USER nobody
ENV PATH="/opt/venv/bin:$PATH"
CMD ["/app/entrypoint.sh"]
