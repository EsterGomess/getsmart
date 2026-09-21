## Table of Contents

- [Description](#description)
- [How to run](#how-to-run)
  - [Building, running Docker and useful commands](#building-running-docker-and-useful-commands)
  - [Database](#database)
- [Diagrams](#diagrams)
- 
# 기억공간 - Gieok Gonggan

This app is built as my MVP project in my post-degrees
in PUC – Rio.

The idea became from my studies, I need a way to
keep my knowledge easily and also keep in my memory.

After looking for ways to keep my knowledge easy to find
and feel less dumped after using IA so much,
I decide to create this app using Zettelkasten methodology,
created by Niklas Luhmann.

So I can learn to put what I learn in my postgreSQL,
and also I can use it to keep my memories easily.

**Enjoy it!**


# Description

This project is a web application built using FastAPI, PostgreSQL, and Docker. 
It serves as a knowledge management system based on the Zettelkasten methodology, allowing users to store, organize, and retrieve their knowledge efficiently.
---

# How to run
This project is built using Python 3.11, FastAPI, PostgreSQL, and Docker.

## Building, running Docker and useful commands

The application runs using Docker and Docker Compose.
The commands below can be used to build, start, stop, restart, inspect, and debug the application containers.

### Build the Docker image

Build the application Docker image:

```bash
docker build -t gonggan .
```

Rebuild the application image using Docker Compose:

```bash
docker compose build
```

Rebuild the image without using the Docker cache:

```bash
docker compose build --no-cache
```

### Start the application

Start the containers:

```bash
docker compose up
```


Build the images and start the containers:

```bash
docker compose up --build
```

Run the database migrations after starting the containers:
```bash
docker compose exec app alembic upgrade head
```

### Stop and remove containers

```bash
docker compose stop
```

Stop and remove the containers:

```bash
docker compose down
```

Stop and remove the containers and volumes:

```bash
docker compose down -v
```

> **Warning:** `docker compose down -v` removes the Docker volumes, including the PostgreSQL database data.

### Restart containers

Restart all running containers:

```bash
docker compose restart
```

Restart only the application container:

```bash
docker compose restart app
```

Restart only the database container:

```bash
docker compose restart db
```

### Check container status

Show the status of the running containers:

```bash
docker compose ps
```

Show the status of all containers, including stopped containers:

```bash
docker compose ps -a
```

### View container logs

View the application logs:

```bash
docker compose logs app
```

View the application logs in real time:

```bash
docker compose logs -f app
```

View the database logs:

```bash
docker compose logs db
```

View the database logs in real time:

```bash
docker compose logs -f db
```

View the logs of all containers in real time:

```bash
docker compose logs -f
```

### Access the application container

Open a shell inside the application container:

```bash
docker compose exec app sh
```

Check the Python version inside the container:

```bash
docker compose exec app python --version
```

### Access PostgreSQL

Open a PostgreSQL shell inside the database container:

```bash
docker compose exec db psql -U fastapi_user -d fastapi_db
```


### Access the application

Once the containers are running, the application is available at:

`http://127.0.0.1:8000`

The FastAPI documentation is available at:

`http://127.0.0.1:8000/docs`

The ReDoc documentation is available at:

`http://127.0.0.1:8000/redoc`

The application health check is available at:

`http://127.0.0.1:8000/health`

---

## Database

The application uses a PostgreSQL database.

### Shows the current revision of the database

```bash
docker compose exec app alembic current
```

### Shows the history of the database migrations

```bash
docker compose exec app alembic history
```

### Shows the current revision of the database

```bash
docker compose exec app alembic current
```

### Shows the latest revision of the database

```bash
docker compose exec app alembic heads
```

### upgrades the database to the latest revision

```bash
docker compose exec app alembic upgrade head
```

### Creates a new migration file

```bash
docker compose exec app alembic revision --autogenerate -m "description of the migration"
```

### Apply the migration to the database

```bash
docker compose exec app alembic upgrade head  
```

---

# Diagrams