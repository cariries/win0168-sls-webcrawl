FROM public.ecr.aws/lambda/python:3.8

ENV CHROMEVERSION=v1.0.0-55
ENV DRIVERVERSION=2.43
ENV BUCKETNAME=

RUN yum install -y unzip && \
    curl -SL https://chromedriver.storage.googleapis.com/${DRIVERVERSION}/chromedriver_linux64.zip > /tmp/chromedriver.zip && \
    curl -SL https://github.com/adieuadieu/serverless-chrome/releases/download/${CHROMEVERSION}/stable-headless-chromium-amazonlinux-2017-03.zip > /tmp/headless-chromium.zip && \
    unzip /tmp/chromedriver.zip -d /opt/ && \
    unzip /tmp/headless-chromium.zip -d /opt/

RUN yum install -y https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
RUN pip install selenium
RUN pip install boto3
COPY *.py ./
CMD [ "main.handler" ]
