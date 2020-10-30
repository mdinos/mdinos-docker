FROM python:3.7.9-slim-buster

USER root
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN pip install gunicorn
RUN apt-get update && apt-get install -y dnsutils curl
WORKDIR /app/src
ENTRYPOINT ["gunicorn"]
CMD ["-b", "0.0.0.0:80", "test-api:app"]
