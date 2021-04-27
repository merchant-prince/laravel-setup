from modules.configuration import ConfigurationAccessorType
from modules.extracts import configure, pull_fresh_laravel_project, generate_configuration_files, \
    configure_environment_variables, preflight_checks, initialize_git_repository, setup_laravel_packages
from modules.generators import setup_directory_structure


class Application:
    def __init__(self) -> None:
        print('Doing some preflight checks...')
        preflight_checks()

        print('Initializing the project configuration...')
        self.__configuration: ConfigurationAccessorType = configure()

    def run(self) -> None:
        print('Setting up the directory structure of the project...')
        setup_directory_structure(self.__configuration('project.name'))

        print('Generating the configuration files for the project...')
        generate_configuration_files(self.__configuration)

        print('Pulling a fresh laravel project...')
        pull_fresh_laravel_project(self.__configuration)

        print('Initializing git for the laravel project...')
        initialize_git_repository(self.__configuration)

        print('Rewriting environment variables for the laravel project...')
        configure_environment_variables(self.__configuration)

        if self.__configuration('project.packages'):
            print('Setting up additional packages...')
            setup_laravel_packages(self.__configuration)

        print("Project successfully set-up. See the project's README.md for more information.")
