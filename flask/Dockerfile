# Dockerfile
FROM python:3.8.6-slim-buster

RUN apt update && apt install -y libaio1 wget
RUN apt install -y gcc python3-dev
RUN apt install -y --reinstall build-essential
RUN apt install -y libopenblas-base liblapack3 libatlas-base-dev gfortran zlib1g-dev libjpeg-dev

RUN pip install --no-cache-dir --upgrade pip
RUN CFLAGS=-O0 pip install --no-cache-dir matplotlib numpy scipy


WORKDIR /app
ADD . /app

RUN        pip install -v --no-cache-dir -r requirements.txt

# server = "python manage.py runserver 0.0.0.0:8000"
#ENTRYPOINT ["pipenv", "run", "server"]
#uwsgi has wggi.py equivalent run.py configured in in app.ini
CMD ["uwsgi", "app.ini"]
