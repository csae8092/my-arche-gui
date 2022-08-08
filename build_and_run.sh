#/bin/bash
clear
docker container stop frd-ac
docker build -t myagui:latest .
echo "##################"
echo "##################"
docker run -it -p 8020:8020 --rm --env-file env.default --name myagui myagui:latest
docker container logs -f myagui