##
# Build an image to run oyente
#
FROM python:2.7.13
ARG SOLC_VERSION=v0.4.20

RUN wget --quiet --output-document /usr/local/bin/solc https://github.com/ethereum/solidity/releases/download/${SOLC_VERSION}/solc-static-linux \
	&& chmod a+x /usr/local/bin/solc

RUN apt-get update \
	&& apt-get install -y software-properties-common \
	&& apt-get install -y unzip

RUN wget --quiet https://github.com/Z3Prover/z3/archive/z3-4.5.0.zip \
	&& unzip z3-4.5.0.zip -d /tmp \
	&& cd /tmp/z3-z3-4.5.0 \
	&& python scripts/mk_make.py --python \
	&& cd build \
	&& make \
	&& make install

RUN wget --quiet https://github.com/melonproject/oyente/archive/master.zip \
	&& unzip master.zip -d /tmp \
	&& mv /tmp/oyente-master/oyente /usr/local/lib/python2.7/site-packages

RUN wget --quiet https://gethstore.blob.core.windows.net/builds/geth-alltools-linux-amd64-1.8.2-b8b9f7f4.tar.gz \
	&& tar -xvf geth-alltools-linux-amd64-1.8.2-b8b9f7f4.tar.gz \
	&& chmod a+x geth-alltools-linux-amd64-1.8.2-b8b9f7f4/* \
	&& mv geth-alltools-linux-amd64-1.8.2-b8b9f7f4/* /usr/bin

WORKDIR /app

RUN pip install --upgrade pip setuptools \
	&& pip install --upgrade pip-tools \
	&& pip install requests

# Copy source
COPY source/contracts/ /app/source/contracts/
COPY source/tools/ /app/source/tools/

# Run the oyente test script
RUN python source/tools/runOyente.py -p

ENTRYPOINT ["npm"]
