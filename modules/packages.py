from re import compile, escape
from subprocess import run

from modules.configuration import ConfigurationAccessorType
from modules.utilities import cd, migrate_database, start_stack, template_path


def setup_horizon(configuration: ConfigurationAccessorType):
    with cd(configuration('project.name')):
        with start_stack():
            run(('./run', 'composer', 'require', 'laravel/horizon'), check=True)
            run(('./run', 'artisan', 'horizon:install'), check=True)
            migrate_database()

        with cd(f"application/core/{configuration('project.name')}/app/Console"):
            with open('Kernel.php', 'r+') as file:
                file_contents = file.read()
                command_regex = compile(r' *' + escape("// $schedule->command('inspire')->hourly();"))
                new_file_contents = command_regex.sub(
                    "        $schedule->command('horizon:snapshot')->everyFiveMinutes();",
                    file_contents
                )

                file.seek(0)
                file.write(new_file_contents)
                file.truncate()

        with cd(f"application/core/{configuration('project.name')}"):
            run(('git', 'add', '*'), check=True)
            run(('git', 'commit', '--message', 'scaffold laravel/horizon package.'), check=True)

        with cd('configuration/supervisor/conf.d'):
            with open('supervisord.conf', 'a') as supervisord_configuration, open(
                    template_path('configuration/supervisor/conf.d/supervisord.horizon.conf')) as horizon_configuration:
                supervisord_configuration.write(f'\n{horizon_configuration.read()}')


def setup_sanctum():
    pass


def setup_scout():
    pass


def setup_socialite():
    pass


def setup_telescope():
    pass
