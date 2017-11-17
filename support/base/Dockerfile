##
# Build a base package for augur-core.
#
# The build process is strucutred this way to encourage fail fast behavior so
# that this image's build will fail earlier for compiling contracts than
# for other pieces
FROM node:8.6.0

WORKDIR /app

# Install basics of the application
COPY package.json /app/package.json
COPY package-lock.json /app/package-lock.json
RUN npm install

# Copy the git info so ContractDeployer can read the hash on deploy
COPY .git/ /app/.git/
COPY ./support/deploy/deploy.sh /app/deploy.sh
COPY ./support/deploy/update-artifacts.sh /app/update-artifacts.sh

# Copy source
COPY tsconfig.json /app/tsconfig.json
COPY typings/ /app/typings/
COPY source/ /app/source/

# build it all
RUN npm run build

ENTRYPOINT [ "npm", "run", "test" ]

