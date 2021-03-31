# ${PROJECT_NAME}


## Architecture

The architecture of the project is as follows:

```
${PROJECT_NAME}                         <--- Root project directory
│
├── application                         <--- Project application directory
│   └── core                            <--- Core application project
│       └── ${PROJECT_NAME}             <--- Laravel project
│
├── configuration                       <--- Configuration directory for all the available services
│   │
│   ├── nginx                           <--- Nginx configuration directory
│   │   ├── conf.d                      <--- Main nginx configuration
│   │   │   ├── default.conf            <--- Application configuration
│   │   │   └── utils.conf              <--- Other services (utilities) configuration
│   │   │
│   │   └── ssl                         <--- Ssl configuration
│   │       ├── ${SSL_KEY_NAME}         <--- Ssl key
│   │       └── ${SSL_CERTIFICATE_NAME} <--- Ssl certificate
│   │
│   └── supervisor                      <--- Supervisor configuration
│       └── conf.d                      <--- Main supervisor configuration
│           └── supervisord.conf        <--- Supervisord configuration
│
├── docker-compose                      <--- Docker-Compose configuration
│   └── services                        <--- Docker-Compose services
│       └── php                         <--- PHP service configuration
│           └── Dockerfile              <--- PHP dockerfile
│
├── docker-compose.yml                  <--- Main docker-compose configuration
└── run                                 <--- Script to run Artisan, Yarn, or Composer
```


## Usage

The project is **started** using ```docker-compose``` in the *root project directory*.

```shell script
$$ docker-compose up
```


### Run

To run **artisan**, **yarn**, or **composer** commands in the project, use the ```run``` script provided in the root directory of the project.

```shell script
# artisan
$$ ./run artisan <COMMAND>

# yarn
$$ ./run yarn <COMMAND>

# composer
$$ ./run composer <COMMAND>
```


## Services

The following services of the project are available at [${PROJECT_DOMAIN}](${PROJECT_DOMAIN}):

| Service       | Port            | Description                                |
|:--------------|:---------------:|:-------------------------------------------|
| Nginx         | 80              | Nginx HTTP service (redirect to HTTPS)     |
|               | 443             | Nginx HTTPS service (serve content)        |
| Adminer       | ${ADMINER_PORT} | Adminer service (DB viewer)                |
| Mailhog       | ${MAILHOG_PORT} | Mail service (viewer / debugger)           |
