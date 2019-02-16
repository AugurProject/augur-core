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

RUN cd /tmp && git clone https://github.com/Z3Prover/z3.git && cd z3 \
	&& python scripts/mk_make.py --python --debug --trace \
	&& cd build \
	&& make -j8 \
	&& make install

RUN wget --quiet https://gethstore.blob.core.windows.net/builds/geth-alltools-linux-amd64-1.8.2-b8b9f7f4.tar.gz \
	&& tar -xvf geth-alltools-linux-amd64-1.8.2-b8b9f7f4.tar.gz \
	&& chmod a+x geth-alltools-linux-amd64-1.8.2-b8b9f7f4/* \
	&& mv geth-alltools-linux-amd64-1.8.2-b8b9f7f4/* /usr/bin

WORKDIR /app

RUN pip install --upgrade pip setuptools \
	&& pip install --upgrade pip-tools \
	&& pip install requests

RUN pip install --no-dependencies git+https://github.com/cryptomental/oyente.git@feature/exclude-selected-vulnerabilities

# Copy source
COPY source/contracts/ /app/source/contracts/
COPY source/tools/ /app/source/tools/

# Run the oyente test script
RUN python source/tools/runOyente.py -p -a -v

ENTRYPOINT ["npm"]
