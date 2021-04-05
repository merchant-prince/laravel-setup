#!/usr/bin/env python3

from modules.configuration import ConfigurationAccessorType
from modules.extracts import configure, countdown, ignition, main_engine_start, orbital_checkout, preflight_checks, \
    takeoff, to_infinity

if __name__ == '__main__':
    print('Doing some preflight checks...')
    preflight_checks()

    print('Initializing the project configuration...')
    configuration: ConfigurationAccessorType = configure()

    print('Setting up the directory structure of the project...')
    ignition(configuration)

    print('Generating the configuration files for the project...')
    main_engine_start(configuration)

    print('Pulling a fresh laravel project...')
    countdown(configuration)

    print('Initializing git for the laravel project...')
    takeoff(configuration)

    print('Rewriting environment variables for the laravel project...')
    orbital_checkout(configuration)

    if configuration('project.packages'):
        print('Setting up additional packages...')
        to_infinity(configuration)

    print("Project successfully set-up. See the project's README.md for more information.")
