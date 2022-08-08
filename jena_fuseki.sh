#/bin/bash

mkdir ${PWD}/fuseki
docker run -d --name fuseki -p 3030:3030 -v ${PWD}/fuseki:/fuseki  -e ADMIN_PASSWORD=admin stain/jena-fuseki