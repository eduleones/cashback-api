# CASHBACK-API

## How to install

**Attention:** Bear in mind this project runs with Python 3.7.3 and FastAPI. It was also developed on Linux Debian 10.3. That's why there are some o.s. packages dependencies, mentioned below.

#### Clone this project


Clone the repository inside the new one.
```
git clone git@github.com:eduleones/cashback-api.git
```

#### Install

In order to start installing  dependencies, environment  and initial setup. We had already simplified this by creating a make command:

```
make install-linux
```

Environment setup  in `.env` file. 


#### Database

You must start the containers with Docker:

```
make docker-compose-up
```
or
```
sudo docker-compose up -d
```

##### Creating tables

Now that you already have your database up and running, it's time to create system tables.

This command below will create all instructions that your database will need:

```
make migrations
```

With instructions created, it's time to apply them (execute within database):

```
make migrate
make initial-data
```


#### Run tests


```
make test
```

## API Docs

You can access the API documentation by running the application server:

```
make runserver
```
and accessing:

http://localhost:8080/docs/

