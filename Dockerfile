FROM ubuntu:18.10

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y locales
RUN apt-get install -y python3 python3-dev python3-pip nginx
RUN pip3 install uwsgi

RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=en_US.UTF-8

ENV LC_ALL=en_US.UTF-8 
ENV LANG=en_US.UTF-8

COPY . /app
WORKDIR /app

RUN pip3 install -r requirements.txt

COPY ./docker/web/b.crt /usr/local/share/ca-certificates/b.crt
RUN update-ca-certificates

ENV FLASK_APP app.py
ENV FLASK_RUN_HOST 0.0.0.0

ENTRYPOINT ["flask"]
CMD ["run"]