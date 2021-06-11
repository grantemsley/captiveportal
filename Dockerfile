FROM python:slim

EXPOSE 8080
STOPSIGNAL SIGTERM

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends nginx && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY nginx.default /etc/nginx/nginx.conf
RUN chown -R nobody:nogroup /var/lib/nginx && chown -R nobody:nogroup /var/log/nginx

COPY entrypoint.sh ./
COPY ./captiveportal ./
RUN chown -R nobody:nogroup /app

RUN mkdir /data && chown nobody:nogroup /data

USER nobody
CMD ["/app/entrypoint.sh"]
