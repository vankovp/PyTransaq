#FROM python:3.9.13-alpine3.16
FROM amancevice/pandas:alpine
RUN ln -s /usr/share/zoneinfo/Europe/Moscow /etc/localtime
WORKDIR /usr/src/app
VOLUME /var/data
COPY requirements.txt /usr/src/app/
RUN pip install -r requirements.txt
WORKDIR /usr/src/app
VOLUME /var/data
COPY *.py *.txt  ./

EXPOSE 80

RUN pip install -r requirements.txt