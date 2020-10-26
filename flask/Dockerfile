# Dockerfile
FROM python:3.8.6-slim-buster as base
RUN apt update && apt install --no-install-recommends  -y build-essential python3-dev \
    libopenblas-base liblapack3 libatlas-base-dev gfortran zlib1g-dev libjpeg-dev
RUN pip install --no-cache-dir --upgrade pip

FROM base as builder
RUN mkdir /install
WORKDIR /install
COPY requirements.txt /requirements.txt
RUN pip install -v --no-cache-dir --target /install -r /requirements.txt
#RUN CFLAGS=-O0 pip install --no-cache-dir matplotlib numpy scipy

FROM base
COPY --from=builder /install /usr/local
WORKDIR /app
ADD . /app


# server = "python manage.py runserver 0.0.0.0:8000"
#ENTRYPOINT ["pipenv", "run", "server"]
#uwsgi has wggi.py equivalent run.py configured in in app.ini
CMD ["uwsgi", "app.ini"]
