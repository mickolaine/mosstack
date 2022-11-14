#-------------------------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See https://go.microsoft.com/fwlink/?linkid=2090316 for license information.
#-------------------------------------------------------------------------------------------------------------
FROM ubuntu:focal

# Configure apt
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get -y install --no-install-recommends apt-utils 2>&1

# Install git, process tools, lsb-release (common in install instructions for CLIs)
RUN apt-get -y install git procps lsb-release build-essential python3-setuptools python3-pip nano

# Install libraries and programs required for mosstack
RUN apt-get -y install source-extractor libcfitsio-dev libraw-dev dcraw libaec-dev libblosc-dev libbrotli-dev

# Install developement tools
RUN pip3 install pylint
RUN pip3 install rope

# Install dependencies which setuptools needs to run
RUN pip3 install cython
RUN pip3 install numpy

RUN pip3 install astropy


# Clean up
RUN apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*
ENV DEBIAN_FRONTEND=dialog

