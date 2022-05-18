## Running the application using Docker-compose
An example containing a demo setup for the app is included in the docker-compose file. Note that this file is not intended for use in production and is only provided to illustrate how the backend and frontend of the app could be connected to a MongoDB instance stored on an external image. Start the docker-compose demo using this command:

```
docker-compose up -d
```
The command will create 3 containers:
- mongodb: starting a mongodb server with support for user authentication (--auth option)
- patientmatcher_cli: the a command-line app, which will connect to the server and populates it with demo data
- patientmatcher_web: a web server running on localhost and port 8000.

The server will be running and accepting requests sent from outside the containers (another terminal or a web browser). Read further down to find out about requests and commands.

To test server responses try to invoke the `metrics` endpoint with the following command:
```
curl localhost:8000/metrics
```

To stop the containers (and the server), run:
```
docker-compose down
```
Make sure that there are no mongo containers running before before running the command again.
Commands:
```
docker ps -a
docker rm <id of the eventual containers' id>
```
<a name="dockerfiles"></a>
## Dockerfile and Dockerfile-server

You might have noticed that the docker-compose - based demo described above is using two different containers for the same application.

### Dockerfile
Provides a generic image for the application, that can be used for launching contaiers to run command line commands (such as add demo data to the database, create a node, etc) or run a development app.

- **Given an instance of MongoDB running on localhost, default port 27017**

#### Example on how to run the standard image to populate the database with demo data

* Build the image: `docker build -t pmatcher-image .`
* Launch a container with the instructions to populate database with demo data: `docker run --rm (--env MONGODB_HOST=host.docker.internal)(--net host) pmatcher-image add demodata`

**--env MONGODB_HOST=host.docker.internal** --> required to be able to access the database on the local Mac OS machine

**--net host** --> required to be able to access the database on a local Linux machine


### Dockerfile-server
Is an image based on the previous one, but contains additional software (gunicorn) and parameters to run patientMatcher in a production environment.

- **Given an instance of MongoDB populated with data, running on localhost, default port 27017**

#### Example on how to launch a production server

* Build the image: `docker build -t server-img -f Dockerfile-server .`
* Launch a the image containing a server running on localhost, port 8000:
```docker run --name server -p 8000:8000 --expose 8000 (--env MONGODB_HOST=host.docker.internal)(--net host) server-img```
