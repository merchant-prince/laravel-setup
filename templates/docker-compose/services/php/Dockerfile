FROM php:fpm

RUN apt-get update \
 && apt-get install -y cron libpq-dev libzip-dev supervisor zip \
 && docker-php-ext-install bcmath pdo_pgsql pgsql pcntl zip \
 && docker-php-ext-configure pgsql \
 && docker-php-ext-configure zip \
 && pecl install redis \
 && docker-php-ext-enable redis \
 && apt-get autoremove \
 && rm -rf /var/lib/apt/lists/*

# Setup composer
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer

# Setup php.ini file
RUN cp "$${PHP_INI_DIR}/php.ini-development" "$${PHP_INI_DIR}/php.ini"

# Change the UID and GID of the www-data so that there are no permission conflicts on the files created or manipulated
# by the container.

ARG USER_ID
ARG GROUP_ID

RUN userdel -f www-data && \
    if getent group www-data; \
    then \
      groupdel www-data; \
    fi && \
    groupadd -g $${GROUP_ID} www-data && \
    useradd -l -u $${USER_ID} -g www-data www-data && \
    install -d -m 0755 -o www-data -g www-data /home/www-data && \
    chown --changes \
          --silent \
          --no-dereference \
          --recursive \
          --from=33:33 \
          $${USER_ID}:$${GROUP_ID} \
          /home/www-data

# Setup cron & associated logging
RUN touch /var/log/application.cron.log \
 && chown www-data:www-data /var/log/application.cron.log \
 && echo "* * * * *    www-data    php /var/www/html/artisan schedule:run >> /var/log/application.cron.log 2>&1" >> /etc/crontab

VOLUME [ "/var/www/html", "/etc/supervisor/conf.d/supervisord.conf" ]

ENTRYPOINT [ "/usr/bin/supervisord" ]

CMD [ "-c", "/etc/supervisor/conf.d/supervisord.conf" ]
