#How to deploy using docker

```console
docker build -f docker/Dockerfile .
docker-compose -f docker/docker-compose.yml --project-directory . up
```