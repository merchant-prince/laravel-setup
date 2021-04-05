# Laravel Setup

![Project Status](https://img.shields.io/badge/status-active-brightgreen?style=flat-square)
&nbsp;&nbsp;&nbsp;&nbsp;
![License](https://img.shields.io/badge/license-GNU%20GPLv3-brightgreen?style=flat-square)

Laravel Setup is a convenient python script used to generate a [Laravel](https://laravel.com) project along with its
development environment. It uses [Docker](https://www.docker.com) for the project infrastructure.

The following services are provided for every generated project:

* **[Nginx](https://www.nginx.com)** (web-server & reverse-proxy)
* **[PHP-FPM](https://www.php.net/manual/en/install.fpm.php)** (PHP engine)
* **[PostgreSQL](https://www.postgresql.org)** (database)
* **[Redis](https://redis.io)** (cache / queue)
* **[Adminer](https://www.adminer.org)** (database viewer)
* **[Mailhog](https://github.com/mailhog/MailHog)** (e-mail viewer / debugger)


### Assumptions

The package author assumes the following:

* The package is being used on a ```linux``` environment.
* Python ```3.9``` is installed on the system.


## Installation

To install the **Laravel Setup** project, you only need to clone the project.

```shell
$ git clone https://github.com/merchant-prince/laravel-setup.git
```


## Usage

To use the script, you need to call the main.py script with the appropriate arguments.

```shell
$ ./main.py setup ProjectName [--domain DOMAIN] [--with [{horizon,telescope}]
```


## Features

A bare-bones Laravel project can be set-up using the following command:

```shell script
$ ./main.py setup LeProject
```

The above command will generate a project in the current working directory hosted at
[https://application.local](https://application.local).


### Custom Domain

If you would like to host your project at a domain other than [https://application.local](https://application.local),
you can pass the ```--domain``` flag with the domain where you would like the project to be hosted.

```shell script
$ ./main.py setup MyApplication --domain example.local
```


#### Note
Add the following to your ```/etc/hosts``` file so that you can view the project at the aforementioned URI.

```
# /etc/hosts

127.0.0.1    application.local      # or any other domain you wish to use for your project
```


### Additional Packages

If you would like to install any (or all) of the following packages, you can specify them using the ```--with``` flag.

The packages that can be installed are:

* [Horizon](https://laravel.com/docs/8.x/horizon)
* [Telescope](https://laravel.com/docs/8.x/telescope)

This can be done as follows:

```shell script
$ ./main.py setup MyProject --with horizon telescope
```


## Further Information

For further information on the generated project, see its README.md file.


## License

[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0)
