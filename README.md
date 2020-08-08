# Laravel Setup

Laravel Setup is a convenient python script used to generate a [Laravel](https://laravel.com) project along with its
development environment. It uses [Docker](https://www.docker.com) for the project infrastructure.

The following services are provided for every generated project:

* **[Nginx](https://www.nginx.com)** (web-server & reverse-proxy)
* **[PHP-FPM](https://www.php.net/manual/en/install.fpm.php)** (PHP engine)
* **[PostgreSQL](https://www.postgresql.org)** (database)
* **[Redis](https://redis.io)** (cache / queue)
* **[Adminer](https://www.adminer.org)** (database viewer)
* **[Mailhog](https://github.com/mailhog/MailHog)** (e-mail viewer / debugger)


## Installation

To install **Laravel Script**, do the following:

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

$ ./.venv/bin/activate
```

* Use ```pip``` to install the dependencies of the project.

```shell script
$ pip install -r requirements.txt
```


## Usage

To use the script, you need to run it using the ```venv``` python. This can be done by either running the
```laravel.py``` script after activating ```venv```, or by using the ```venv``` python binary ```.venv/bin/python```.

```shell script
$ ./.venv/bin/activate
$ python laravel.py

# OR

$ ./.venv/bin/python laravel.py
```

The script can be run as follows:

```shell script
$ python laravel.py setup ProjectName

# OR

$ ./.venv/bin/python laravel.py setup ProjectName
```

For *help*, pass the ```-h``` or ```--help``` argument when calling the script.

```shell script
$ python laravel.py --help
```


## Features

A normal Laravel project can be set-up using the following command:

```shell script
$ python laravel.py setup LeProject
```

The above command will generate a project hosted at [https://application.local](https://application.local).


#### Note
Add the following to your ```/etc/hosts``` file so that you can view the project at the aforementioned URI.

```shell script
# /etc/hosts

127.0.0.1    application.local
```


### Custom Domain

If you would like to host your project at a domain other than [https://application.local](https://application.local),
you can pass the ```--domain``` flag with the domain where you would like the project to be hosted.

```shell script
$ python laravel.py setup MyApplication --domain example.local
```


### Additional Packages

If you would like to install any (or all) of the following packages, you can specify them using the ```--with``` flag.

The packages that can be installed are:

* [Authentication (UI)](https://laravel.com/docs/7.x/frontend)
* [Horizon](https://laravel.com/docs/7.x/horizon)
* [Telescope](https://laravel.com/docs/7.x/telescope)

This can be done as follows:

```shell script
$ python laravel.py setup MyProject --with authentication horizon telescope
```


## License

[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0)