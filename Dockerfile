FROM python:3.6.0
MAINTAINER Richard Chien <richardchienthebest@gmail.com>

RUN mkdir /veripress
WORKDIR /veripress
COPY veripress veripress
COPY veripress_cli veripress_cli
COPY setup.py setup.py
COPY README.md README.md
COPY MANIFEST.in MANIFEST.in
RUN pip install . gevent

VOLUME ["/instance"]
WORKDIR /instance
ENTRYPOINT ["veripress"]
