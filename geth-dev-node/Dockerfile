FROM ethereum/client-go:latest
COPY genesis.json /app/genesis.json
RUN echo "p" > /app/password.txt
RUN geth makedag 0 /app/.ethash

WORKDIR /
COPY start.sh /start.sh
RUN chmod +x /start.sh
ENTRYPOINT /start.sh
