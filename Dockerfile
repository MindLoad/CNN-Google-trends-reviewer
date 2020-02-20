FROM python:3.8-alpine

MAINTAINER Ivan Tk <...>

# PYTHONUNBUFFERED: Force stdin, stdout and stderr to be totally unbuffered. (equivalent to `python -u`)
# PYTHONHASHSEED: Enable hash randomization (equivalent to `python -R`)
# PYTHONDONTWRITEBYTECODE: Do not write byte files to disk, since we maintain it as readonly. (equivalent to `python -B`)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONHASHSEED=random

# Dockerize
ENV DOCKERIZE_VERSION=v0.6.1
ADD https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz /dockerize.tar.gz
RUN tar -C /usr/local/bin -xzvf /dockerize.tar.gz && rm -f /dockerize.tar.gz

# Install system dependencies
RUN apk update && apk add postgresql-dev gcc musl-dev

# Insall ssh agent
RUN apk add --no-cache openssh make && \
	ssh-keygen -A && \
	echo 'root:root' | chpasswd && \
	sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
	sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
	sed -i -e 's/#*Port 22/Port 2227/' /etc/ssh/sshd_config && \
    sed -i '/AcceptEnv */d' /etc/ssh/sshd_config && \
    echo "export VISIBLE=now" >> /etc/profile

# Install Pipenv
ARG packages
RUN apk --update add ${packages} && rm -rf /var/cache/apk/*
RUN pip install --upgrade pip
RUN pip install pipenv

RUN mkdir /code
COPY . /code/

WORKDIR /code
RUN pipenv install -d --deploy --system --ignore-pipfile

WORKDIR /code/cnn
CMD ["/bin/sh", "/code/start.sh"]
