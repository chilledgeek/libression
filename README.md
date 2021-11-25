# libression

minio used to expose files to http link so can read from html

now just do docker-compose up to get s3 and redis (not tested redis yet)

## Minio
- docker:
  - `docker run -v /<path>/<to>/<your>/<photosdir>:/data -p 9000:9000 quay.io/minio/minio server /data`
  - e.g. `sudo docker run -v /home/e/Desktop/temp:/data -p 9000:9000 -p 9001:9001 quay.io/minio/minio server /data --console-address ":9001"
`