FROM python:3.10-slim

COPY requirements.txt /tmp/pip-tmp/
RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
 && rm -rf /tmp/pip-tmp

WORKDIR /var/www/html/
CMD npm run build

WORKDIR /var/www/html/src
CMD gunicorn -b 0.0.0.0:80 app:server