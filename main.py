#!/usr/bin/env python3

from modules.configuration import ConfigurationAccessorType
from modules.extracts import configure, pull_fresh_laravel_project, generate_configuration_files, \
    configure_environment_variables, preflight_checks, initial_git_commit, setup_laravel_packages
from modules.generators import setup_directory_structure

if __name__ == '__main__':
    print('Doing some preflight checks...')
    preflight_checks()

    print('Initializing the project configuration...')
    configuration: ConfigurationAccessorType = configure()

    print('Setting up the directory structure of the project...')
    setup_directory_structure(configuration('project.name'))

    print('Generating the configuration files for the project...')
    generate_configuration_files(configuration)

    print('Pulling a fresh laravel project...')
    pull_fresh_laravel_project(configuration)

    print('Initializing git for the laravel project...')
    initial_git_commit(configuration)

    print('Rewriting environment variables for the laravel project...')
    configure_environment_variables(configuration)

    if configuration('project.packages'):
        print('Setting up additional packages...')
        setup_laravel_packages(configuration)

    print("Project successfully set-up. See the project's README.md for more information.")
