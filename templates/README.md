# ${project_name}


## Architecture

The architecture of the project is as follows:

```
${project_name}    <--- Root project directory
│
├── application    <--- Application directory
│   └── ${project_name}    <--- Laravel project
│
├── configuration    <--- Configuration directory for all the available services
│   │
│   ├── nginx    <--- Nginx configuration directory
│   │   ├── conf.d    <--- Main nginx configuration
│   │   │   ├── default.conf    <--- Application configuration
│   │   │   └── utils.conf    <--- Other services (utilities) configuration
│   │   │
│   │   └── ssl    <--- Ssl configuration
│   │       ├── certificate.pem    <--- Ssl certificate
│   │       └── key.pem    <--- Ssl key
│   │
│   └── supervisor    <--- Suervisor configuration
│       └── conf.d    <--- Main supervisor configuration
│           └── supervisord.conf    <--- Supervisord configuration
│
├── docker-compose    <--- Docker-Compose configuration
│   └── services    <--- Docker-Compose services
│       └── php    <--- PHP service configuration
│           └── Dockerfile    <--- PHP dockerfile
│
├── docker-compose.yml    <--- Main docker-compose configuration
└── run    <--- Script to run Artisan, Yarn, or Composer
```


## Usage

The project is **started** using ```docker-compose``` in the *root project directory*.

```shell script
$$ docker-compose up
```


### Run

To run **artisan**, **yarn**, or **composer** in the project, use the ```run``` script provided in the root project
directory; *from the root directory*.

```shell script
# artisan
$$ ./run artisan COMMAND

# yarn
$$ ./run yarn COMMAND

# composer
$$ ./run composer COMMAND
```


## Services

The following services of the stack are available at [${project_domain}](${project_domain}):

| Service       | Port | Description                                |
|:--------------|:----:|:-------------------------------------------|
| Nginx         | 80   | Nginx HTTP service (redirect to HTTPS).    |
|               | 443  | Nginx HTTPS service (serve content).       |
| PHP           | 9000 | PHP service (PHP processing).              |
| Postgresql    | 5432 | PostgreSQL service (main database).        |
| Adminer       | 8080 | Adminer service (DB viewer).               |
| Mailhog       | 8025 | Mail service (viewer / debugger).          |
| Redis         | -    | Caching.                                   |
