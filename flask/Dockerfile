# Dockerfile
FROM python:3.11-slim-bullseye AS build
RUN apt update && apt install --no-install-recommends  -y build-essential \
    libopenblas-base liblapack3 libatlas-base-dev gfortran zlib1g-dev libjpeg-dev \
    libpcre3 libpcre3-dev
ENV PIP_EXTRA_INDEX_URL=https://www.piwheels.org/simple
RUN addgroup --gid 1000 appuser
RUN useradd -rm -d /home/appuser -s /bin/bash -g 1000 -G sudo -u 1000 appuser
USER appuser
WORKDIR /home/appuser
ENV VIRTUAL_ENV=/home/appuser/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"
RUN pip install -v --no-cache-dir --upgrade pip
RUN pip install -v --no-cache-dir --upgrade wheel
COPY requirements.txt .
RUN pip install -v --no-cache-dir  -r requirements.txt

#FROM python:3.11-slim-bullseye@sha256:5a67c38a7c28ad09d08f4e153280023a2df77189b55af7804d7ceb96fee6a68f
FROM python:3.11-slim-bullseye
WORKDIR /app
COPY --chown=1000:1000 --from=build /home/appuser/venv /home/appuser/venv
ADD --chown=1000:1000 . /app
# Change to copy for 'prod'
ENV PATH="${PATH}:/home/appuser/venv/bin"

#uwsgi has wsgi.py equivalent run.py configured in in app.ini
ENV MPLCONFIGDIR=/tmp/
CMD ["uwsgi", "app.ini"]
