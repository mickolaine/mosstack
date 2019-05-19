FROM python:3.6-stretch
ADD . /mosstack
WORKDIR /mosstack
RUN apt-get update
RUN apt-get -y install sextractor build-essential bash libcfitsio-dev libcfitsio5 libraw-dev libraw15
RUN pip install .
RUN python setup.py install
#CMD ["python", "test/fullprocess.py"]
CMD ["/bin/bash"]
