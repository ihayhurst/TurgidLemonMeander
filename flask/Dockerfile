# Dockerfile
FROM python:3.11-slim-bullseye as base
RUN apt update && apt install --no-install-recommends  -y build-essential \
    libopenblas-base liblapack3 libatlas-base-dev gfortran zlib1g-dev libjpeg-dev \
    libpcre3 libpcre3-dev
ENV PIP_EXTRA_INDEX_URL=https://www.piwheels.org/simple
RUN addgroup --gid 1000 appuser
RUN useradd -rm -d /home/appuser -s /bin/bash -g 1000 -G sudo -u 1000 appuser
USER appuser
WORKDIR /home/appuser
RUN python3 -m venv venv
RUN . venv/bin/activate
ENV PATH="${PATH}:/home/appuser/.local/bin"
RUN pip install -v --no-cache-dir --upgrade pip
RUN pip install -v --no-cache-dir --upgrade wheel

#RUN CFLAGS=-O0 pip install --no-cache-dir matplotlib numpy scipy


FROM base
WORKDIR /app
ADD . /app

RUN pip install -v --no-cache-dir  -r requirements.txt

#uwsgi has wsgi.py equivalent run.py configured in in app.ini
ENV MPLCONFIGDIR=/tmp/
CMD ["uwsgi", "app.ini"]
