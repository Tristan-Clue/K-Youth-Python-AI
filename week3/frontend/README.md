## Intructions

docker build ./ -t frontend:1.0
docker run -p 8000:8000 frontend:1.0

Command: `docker build [context] -t [image_name:tag]`
context: The build context that is sent to the Docker daemon (Used by COPY)
image_name: Name of the image
tag: Version/Label of the image (1.0, 1.5, 2.0, latest, etc. etc.)

Command: `docker run -p [host_port]:[container_port] [image_name:tag]`
Port mapping: `-p 8000 : 8000` Setting up port where traffic will arrive on the local machine (host_port) and the target port where the app is listening from inside the container environment (container_port)

Alternative commands when running:
`--rm` : Auto removes container when stopped. Use `docker ps -a` to check pile up
`--name` : Names your container