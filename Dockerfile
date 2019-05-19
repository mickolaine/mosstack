FROM python:3.6-stretch
ADD . /mosstack
WORKDIR /mosstack
RUN apt update
RUN apt -y install sextractor build-essential
RUN pip install .
CMD [mosstack]