FROM centos:7
MAINTAINER Hans Keeler <hans.keeler@cfpb.gov>

ENV PY_VER 2.7.12
ENV PY_NAME Python-$PY_VER
ENV PY_FILE $PY_NAME.tgz

# Install latest Python 2.7
RUN yum update -y && \
    yum install -y bzip2-devl openssl-devel sqlite-devel zlib-dev gcc && \
    yum groupinstall -y development && \
    cd /tmp && \
    curl -O https://www.python.org/ftp/python/$PY_VER/$PY_FILE && \
    tar -xzf $PY_FILE && \
    cd $PY_NAME && \
    ./configure && \
    make -s && \
    make altinstall && \
    curl https://bootstrap.pypa.io/get-pip.py | python2.7

# Add all app-specific files
ADD app.py requirements.txt rules.yaml /opt/grasshopper-parser/
ADD conf/ /opt/grasshopper-parser/conf/

WORKDIR /opt/grasshopper-parser

RUN pip install -r requirements.txt

USER nobody 

EXPOSE 5000

CMD ["gunicorn", "-c", "conf/gunicorn.py", "-b", "0.0.0.0:5000", "app:app"]
