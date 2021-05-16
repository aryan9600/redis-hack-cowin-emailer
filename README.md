# Cowin Emailer

 Vaccinaction slots in India are often full and people don't really get a fair chance to book their slot with them having to constantly check the registration website. This project aims to alert users living in India about vaccine availbility, by sending them an email.
 
 Users need to register themselves using the CLI and verify their email using an OTP. After that, users will automatically be notified if any vaccination slots open up in their district.
 
 ## Usage
 * To register yourself, run: `redis-hack register --email "hey@email.com", --state "my state" --district "my district"`
 * After running this, you shall recieve a OTP code on your email.
 * To verify yourself, run: `redis-hack verify --email "hey@email.com" --code "code"`
 * That's it! You'll get a mail as soon as a slot opens up.

## Screenshots
![About](https://github.com/aryan9600/redis-hack-cowin-emailer/blob/main/screenshots/Screen%20Shot%202021-05-16%20at%2010.07.06.png)
![Register](https://github.com/aryan9600/redis-hack-cowin-emailer/blob/main/screenshots/Screen%20Shot%202021-05-16%20at%2010.06.05.png)
![Verify](https://github.com/aryan9600/redis-hack-cowin-emailer/blob/main/screenshots/Screen%20Shot%202021-05-16%20at%2010.07.00.png)

## Tech Stack
* __Python/FastAPI__: Backend server
* __Celery__: Task queue
* __Redis__: Message broker and datastore
* __RediJSON__: Store JSON documents
* __Docker/docker-compose__: Packaging and deployment
* __Rust__: CLI for user

## Architecture
![Architecture](https://github.com/aryan9600/redis-hack-cowin-emailer/blob/main/screenshots/arch.png)


## Redis Commands
* To check if the key "users/districts" exists: `EXISTS users`/`EXISTS districts`
* To add the key "users/districts" with a JSON document: `JSON.SET users . {}`/`JSON.SET districts . {}`
* To register a user: `JSON.SET users '["{email}"]' {user_obj}`
* To check if a district ID exists: `JSON.GET districts '["district_id"]'`. (Compare this value to NULL to check for existence)
* To add an user email to a district: `JSON.ARRAPPEND districts '["district_id"]' {user_email}`
* To looup a user by their email: `JSON.GET users '["{email}"]'`
* To mark a user as verified: `JSON.SET users '["{email}"]'['verified'] True`
* To get all emails belonging to a district: `JSON.GET districts '["district_id"]`
* To get all users via list of emails: `JSON.GET users '["{email1}"]' '["{email2}"]' ...`
* To store the notification status of a slot for a user: `JSON.ARRAPPEND users '["{email}"]'["session_ids"] session_id`

## Installation Steps

### Backend
The entire backend is dockerized with the help of docker-compose into three services:
* `web`: This service runs the FastAPI server
* `celery`: This service runs the celery worker
* `worker`: This service starts the runner to fetch slots and send emails.

To have the backend up and running run `docker-compose up --build` from inside the `backend` directory. Make sure you have a `.env` file similar to the `.env.template`.
To have the backend running properly, you need to have a Redis server loaded with the RediJSON module running. This project uses the Redis Cloud Enterprise Service for the same, but you can also use the [`redismod`](https://github.com/RedisLabsModules/redismod) image for the same. In that case, make sure to update the `.env` file accordingly or you can add it as a service to the `docker-compose.yml` itself, like:
```yml
- redis:
  image: redislabs/redismod
  ports:
      - 6379:6379
```

### CLI
The binary for macOS and Linux are available in the release section of this repo, if you just want to use it.
The CLI is written in Rust, so you need to have [`rustc`](https://www.rust-lang.org/tools/install) installed on your machine to build from source:
* `cd cli`
* `cargo build --release`
