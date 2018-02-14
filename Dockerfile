#
# Docker image to run nduja
#


# Set the base image
FROM ubuntu:artful

# Dockerfile author / maintainer
MAINTAINER Mirko Bez <mirko.bez@studenti.unipd.it>

RUN apt-get update && \
    apt-get install dirmngr -y && \
    # Following the instructions for ubuntu given at 
    # https://git.skewed.de/count0/graph-tool/wikis/installation-instructions#gnulinux
    echo "deb http://downloads.skewed.de/apt/artful artful universe" >> /etc/apt/sources.list && \
    echo "deb-src http://downloads.skewed.de/apt/artful artful universe" >> /etc/apt/sources.list && \
    apt-key adv --keyserver pgp.skewed.de --recv-key 612DEFB798507F25 && \
    apt-get update && \
    apt-get install python3 -y && \
    apt-get install -y python3-graph-tool && \
    apt-get install python3-pip -y && \
    rm -rf /var/lib/apt/lists/*  && \
    apt-get remove dirmngr -y && \
    apt-get remove -y && \
    apt-get autoclean -y && \ 
    apt-get autoremove -y
    
RUN mkdir project
    
VOLUME ["project"]
COPY requirements.txt ./project
WORKDIR project/


RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .
    


# Default Command
CMD ["python3", "./Nduja",  "-c",  "conf.json"] 
