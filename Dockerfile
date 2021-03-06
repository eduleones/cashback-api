FROM python:3.7.3-slim

# The enviroment variable ensures that the python output is set straight
# to the terminal without buffering it first
ENV PYTHONUNBUFFERED 1

ARG UID
ARG GID
ARG COMMAND
ENV RUN_COMMAND=${COMMAND}

RUN echo "Container UID: $UID"
RUN echo "Container GID: $GID"
RUN echo "run_command= $RUN_COMMAND"

# If packages are added/removed here, please also update the packages
# list on requirements/linux.apt, so that the development environment
# keep working .
RUN apt-get update \
 && apt-get install -y --no-install-recommends  \
 ca-certificates openssl build-essential apt-utils \
 libssl-dev zlib1g-dev libbz2-dev strace libreadline-dev \
 libsqlite3-dev wget curl llvm libncurses5-dev tcptraceroute \
 libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python-openssl \
 libpq-dev libcurl4-openssl-dev libssl-dev tree python-pycurl \
 libgnutls28-dev procps htop inetutils-ping ncdu inetutils-telnet \
 net-tools iproute2 nmap strace vim -y \
 && apt-get -y autoremove \
 && rm -fr /var/lib/apt/lists/* \
 && rm -fr /var/cache/apt/archives/*

RUN mkdir /tmp/requirements
COPY requirements/* /tmp/requirements/

RUN tree /tmp/requirements \
  && pip install --upgrade pip \
  && pip install -r /tmp/requirements/base.txt \
  && rm -fr /root/.cache

RUN groupadd -r -g "$GID" appuser; useradd -l --create-home -u "$UID" -g "$GID" appuser
WORKDIR /home/appuser
COPY . /home/appuser

RUN /bin/bash -l -c 'chown -R "$UID:$GID" /home/appuser'

USER appuser
RUN echo "User details: $(id)" && ls -la /home/appuser

EXPOSE 8080

ENTRYPOINT make ${RUN_COMMAND}
