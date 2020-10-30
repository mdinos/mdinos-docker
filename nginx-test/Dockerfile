FROM nginx:1.18.0

USER root
COPY ./www/ /var/www/html/
COPY ./nginx/nginx.conf /etc/nginx/
RUN apt-get update && apt-get install -y dnsutils curl

CMD ["nginx", "-g", "daemon off;"]
