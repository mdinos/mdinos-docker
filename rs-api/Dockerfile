FROM ubuntu:19.04

USER root

RUN apt-get -y update && \
    apt-get -y install \ 
    python3-pip \
    python3-dev

RUN echo "Installed packages, starting app."

COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["rs_api.py"]
