# User service


## How to run

Run

````
$ cp .env.sample_dev .env
$ cp .env.db.sample_dev .env.db
$ docker-compose up -d --build
````

and go to http://localhost:8000/docs

## How to run tests

````
$ docker-compose exec app python -m pytest app/tests
````
