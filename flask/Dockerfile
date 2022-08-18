# Dockerfile
FROM python:3.10-slim-bullseye as base
ENV PIP_EXTRA_INDEX_URL=https://www.piwheels.org/simple
RUN apt update && apt install --no-install-recommends  -y build-essential python3-dev \
    libopenblas-base liblapack3 libatlas-base-dev gfortran zlib1g-dev libjpeg-dev \
    libpcre3 libpcre3-dev
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
