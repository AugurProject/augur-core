FROM augur/augur-core:latest

COPY ./support/deploy/start.sh /app/start.sh
COPY ./support/deploy/transform-output.sh /app/transform-output.sh

ENTRYPOINT [ "bash", "./start.sh" ]
