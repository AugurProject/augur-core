FROM augurproject/augur-core:latest

# install dependencies
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip setuptools \
	&& pip install --upgrade pip-tools \
	&& pip install -r requirements.txt

WORKDIR /app

ENTRYPOINT [ "npm", "run", "test:unit" ]
