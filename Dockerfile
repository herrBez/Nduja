#
# Docker image to run nduja
#


# Set the base image
FROM ubuntu:artful

# Dockerfile author / maintainer
MAINTAINER Mirko Bez <mirko.bez@studenti.unipd.it>

RUN apt-get update && \
    apt-get install python3 -y && \
    apt-get install python3-pip -y && \
    rm -rf /var/lib/apt/lists/*  && \
    apt-get remove -y && \
    apt-get autoclean -y && \ 
    apt-get autoremove -y

    
RUN mkdir project

VOLUME ["project"]
COPY requirements.txt ./project
WORKDIR project/


RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install --upgrade web3


COPY . .
    


# Default Command
CMD ["python3", "./Nduja",  "-c",  "conf.json"] 
