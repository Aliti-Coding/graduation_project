FROM apache/spark-py:latest
USER 0
RUN apt-get install -y git 
COPY ./requirements.txt /tmp/requirements.txt
RUN pip install -r tmp/requirements.txt