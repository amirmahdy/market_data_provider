FROM nginx:1.19.0-alpine

RUN mkdir /src
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/
WORKDIR /src
