##
# Build a base package for augur-core.
#
# The build process is structured this way to encourage fail fast behavior so
# that this image's build will fail earlier for compiling contracts than
# for other pieces
FROM python:2.7.13-stretch
ARG SOLC_VERSION=v0.4.20

RUN curl -sL https://deb.nodesource.com/setup_8.x | bash - \
	&& apt-get install -y nodejs

RUN apt-get update && apt-get install -y unzip libz3-dev

RUN wget --quiet https://github.com/cryptomental/solidity/files/2020750/solc.zip \
	&& unzip solc.zip -d /usr/local/bin && chmod a+x /usr/local/bin/solc

COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --upgrade pip setuptools \
	&& pip install --upgrade pip-tools \
	&& pip install -r requirements.txt


# Install basics of the application
COPY package.json /app/package.json

RUN npm install
COPY .soliumrc.json /app/.soliumrc.json
COPY .soliumignore /app/.soliumignore
COPY tsconfig.json /app/tsconfig.json
COPY typings/ /app/typings/
COPY source/contracts/ /app/source/contracts/
COPY source/deployment/compileContracts.ts /app/source/deployment/compileContracts.ts
COPY source/libraries/CompilerConfiguration.ts /app/source/libraries/CompilerConfiguration.ts
COPY source/libraries/DeployerConfiguration.ts /app/source/libraries/DeployerConfiguration.ts
COPY source/libraries/NetworkConfiguration.ts /app/source/libraries/NetworkConfiguration.ts
COPY source/libraries/ContractCompiler.ts /app/source/libraries/ContractCompiler.ts

# Enable SMT
RUN rgrep "pragma solidity" source/contracts/ | cut -d':' -f1 | xargs sed -i '1ipragma experimental SMTChecker;'

# Do not run SMT on quarantined contracts
COPY source/support/test/smt/quarantine.txt quarantine.txt
RUN while read contract; do sed -i '/pragma experimental SMTChecker/d' ${contract}; done<quarantine.txt 

# Patch contract compiler to use SMT enabled solc instead of solc.js
COPY source/support/test/smt/smt.patch smt.patch
RUN git apply smt.patch

# Lint
RUN npm run lint

# Build first chunk
RUN npm run build:source
RUN npm run build:contracts

COPY source/libraries/ContractInterfacesGenerator.ts /app/source/libraries/ContractInterfacesGenerator.ts
COPY source/tools/generateContractInterfaces.ts /app/source/tools/generateContractInterfaces.ts

# Build contract interfaces
RUN npm run build:source
RUN npm run build:interfaces

# Copy source
COPY source/ /app/source/
COPY tests/ /app/tests/

# Copy the git info so ContractDeployer can read the hash on deploy
RUN npm run build:source
COPY .git/ /app/.git/

ENTRYPOINT ["npm"]
