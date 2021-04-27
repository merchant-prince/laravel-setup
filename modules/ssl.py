from os import getcwd
from pathlib import Path
from shutil import move
from subprocess import run

from modules.utilities import cd, project_path, tmpdir


class Generator:
    def __init__(self, *, domain: str, certificate_name: str, key_name: str) -> None:
        self.__domain: str = domain
        self.__certificate_name: str = certificate_name
        self.__key_name: str = key_name

        self.__src_dirname: str = 'minica_src'
        self.__binary_name: str = 'minica'
        self.__binary_directory: Path = project_path('tools/ssl')

    def binary_is_present(self) -> bool:
        return project_path(f'tools/ssl/{self.__binary_name}').is_file()

    def build_binary(self) -> None:
        with tmpdir():
            run(('git', 'clone', 'https://github.com/jsha/minica.git', self.__src_dirname))

            with cd(self.__src_dirname):
                run(
                    (
                        'docker', 'run',
                        '--rm',
                        '--mount', f'type=bind,source={getcwd()},target=/usr/src/myapp',
                        '--workdir', '/usr/src/myapp',
                        'golang:1.14',
                        'go', 'build'
                    ),
                    check=True
                )

                move(Path(self.__binary_name).absolute(),
                     Path(f'{self.__binary_directory}/{self.__binary_name}').absolute())

    def generate(self) -> None:
        project_certificates_directory: str = getcwd()

        with cd(self.__binary_directory):
            generated_certificates_directory: Path = Path(self.__domain)

            try:
                run((f'./{self.__binary_name}', '--domains', f'{self.__domain},*.{self.__domain}'))

                with cd(generated_certificates_directory):
                    move(Path('cert.pem').absolute(), f'{project_certificates_directory}/{self.__certificate_name}')
                    move(Path('key.pem').absolute(), f'{project_certificates_directory}/{self.__key_name}')
            finally:
                if generated_certificates_directory.is_dir():
                    generated_certificates_directory.rmdir()
