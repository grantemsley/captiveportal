FROM python:alpine

EXPOSE 8080
STOPSIGNAL SIGTERM

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update && apk add nginx

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY nginx.default /etc/nginx/nginx.conf
RUN chown -R nobody:nobody /var/lib/nginx && chown -R nobody:nobody /var/log/nginx

COPY entrypoint.sh ./
COPY ./captiveportal ./captiveportal/
RUN chown -R nobody:nobody /app

RUN mkdir /data && chown nobody:nobody /data

USER nobody
CMD ["/app/entrypoint.sh"]
