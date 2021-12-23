FROM python:3.10-slim-bullseye

COPY files/etc/apt/ /etc/apt/

# runtime setup
ARG VERSION
ENV DOCKER_RPI_GPIO_VERSION ${VERSION}
ENV PIP_EXTRA_INDEX_URL=https://www.piwheels.org/simple
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /usr/lib/python3/dist-packages

ADD requirements.txt /root/
WORKDIR /root
RUN pip install pip --upgrade && \
    pip install -r requirements.txt
ADD *.py /root/

ENV TZ=Europe/London
RUN ln -snf /usr/share/timezone/$TZ /etc/localtime && echo $TZ >/etc/timezone

VOLUME ["/data-log"]
CMD ["python3", "log.py"]
