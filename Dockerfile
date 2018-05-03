FROM python:3.6-slim

MAINTAINER Mirko Bez <mirko.bez@studenti.unipd.it>
LABEL A simple python image

RUN mkdir project

VOLUME ["project"]
COPY requirements.txt ./project
WORKDIR project/


RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

# Default Command
CMD ["python3", "./Nduja",  "-c",  "conf.json"] 
