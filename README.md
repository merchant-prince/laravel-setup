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
* The python version being used for the project is ```3.8.*```.


## Installation

To install the **Laravel Setup** project, do the following:

* Clone the project.

```shell script
$ git clone https://github.com/merchant-prince/laravel-setup.git
```

* Go to the project directory.

```shell script
$ cd laravel-setup
```

* Setup ```venv``` and activate it.

```shell script
$ python -m venv .venv

$ . .venv/bin/activate
```

* Use ```pip``` to install the dependencies of the project.

```shell script
$ pip install -r requirements.txt
```

 * Deactivate ```venv```.
 
 ```shell script
$ deactivate
```


## Usage

To use the script, you need to run it using the ```venv``` python.
In the examples below, we are using the ```venv``` python binary found in ```.venv/bin/python```.

```shell script
$ .venv/bin/python laravel.py setup [-h] [--domain DOMAIN] [--with [{authentication,dusk,horizon,telescope}]] [--jetstream {inertia,inertia.teams,livewire,livewire.teams}] [--development] ProjectName
```


## Features

A normal Laravel project can be set-up using the following command:

```shell script
$ .venv/bin/python laravel.py setup LeProject
```

The above command will generate a project hosted at [https://application.local](https://application.local).


#### Note
Add the following to your ```/etc/hosts``` file so that you can view the project at the aforementioned URI.

```
# /etc/hosts

127.0.0.1    application.local
```


### Custom Domain

If you would like to host your project at a domain other than [https://application.local](https://application.local),
you can pass the ```--domain``` flag with the domain where you would like the project to be hosted.

```shell script
$ .venv/bin/python laravel.py setup MyApplication --domain example.local
```

You should then add the appropriate entries in your ```/etc/hosts``` file.


### Additional Packages

If you would like to install any (or all) of the following packages, you can specify them using the ```--with``` flag.

The packages that can be installed are:

* [Authentication (UI)](https://laravel.com/docs/8.x/frontend)
* [Dusk](https://laravel.com/docs/8.x/dusk)
* [Horizon](https://laravel.com/docs/8.x/horizon)
* [Telescope](https://laravel.com/docs/8.x/telescope)

This can be done as follows:

```shell script
$ .venv/bin/python laravel.py setup MyProject --with authentication dusk horizon telescope
```


#### Jetstream

If you would like to install the ```laravel/jetstream``` package, you can do so using the ```--jetstream``` flag with
the appropriate *stack* to install, and whether to include *teams* support.

This can be done as follows:

```shell script
# installing a laravel project with jetstream -- with the inertia stack and teams support
$ .venv/bin/python laravel.py setup ProjecTatum --jetstream inertia.teams
```


#### Development Version

If you would like to install the **development** version of the laravel framework, you can do so by passing the
```--development``` flag.

```shell script
$ .venv/bin/python laravel.py setup ProjecTatum --development
```


## Further Information

For further information on the generated project, see its README.md file (in the project root).


## License

[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0)
