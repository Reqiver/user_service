# Dockerfile
FROM python:3.11.2-buster

ARG RUNNING_PORT

ENV RUNNING_PORT=${RUNNING_PORT}

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

EXPOSE ${RUNNING_PORT}
ENTRYPOINT ["./docker-entrypoint.sh"]
