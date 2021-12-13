# Libression

## About this project
- Self-hosting media organiser
- Written in python, developed in linux

## Setup
### Minio
- Minio used to serve content from a directory as an S3 object store (so our web app can interact with)
- Install and starting up locally on linux (amd64) ([guide](https://min.io/download#/linux)):
  - ```
    wget https://dl.min.io/server/minio/release/linux-amd64/minio
    chmod +x minio
    MINIO_ROOT_USER=admin MINIO_ROOT_PASSWORD=password ./minio server /home/e/Desktop/temp --console-address ":9001"
    ```
- Alternative, use docker (for CI):
  - `docker run -v /<path>/<to>/<your>/<photosdir>:/data -p 9000:9000 quay.io/minio/minio server /data`
  - e.g. `sudo docker run -v /home/e/Desktop/temp:/data -p 9000:9000 -p 9001:9001 quay.io/minio/minio server /data --console-address ":9001"

## Meaning behind the name Libression:
- Librarian (organiser)
- Liberate (open source, self-hosting)
- Impression (media/photos/videos)
- (coined by @yaxxie)
