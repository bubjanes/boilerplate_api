# Build a Docker image
Place this docker file in the root directory and use the following commands to create and publish your docker image to Docker Hub. 

## From Docker docs...

```
docker build --tag bulletinboard:1.0 .
```

## Test it before pushing to docker hub

```
docker container run --publish 5000:5000 --name bb bulletinboard:1.0
```

## share images on Docker Hub

```
docker tag bulletinboard:1.0 <Your Docker ID>/bulletinboard:1.0
```

```
docker push <Your Docker ID>/bulletinboard:1.0
```
