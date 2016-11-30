import fastentrypoints
from setuptools import setup, find_packages
from setuptools.command.install import install

install_requirements = ['psutil']

version = '0.8.0'

try:
    import importlib
except ImportError:
    install_requirements.append('importlib')

try:
    import PyQt5
except ImportError:
    raise RuntimeError("Please install PyQt5 via your system package manager")


class InstallSystemdServiceFileInstall(install):
    """
    Installs systemd service user file during install.
    """

    def install_systemd_service(self):
        import os

        if os.path.isdir('/etc/systemd/user/'):
            from pkg_resources import Requirement, resource_filename
            from shutil import copy2
            service_path = resource_filename(Requirement.parse("actor"),
                                             "actor/static/actor.service")
            copy2(service_path, '/etc/systemd/user/')

    def run(self):
        install.run(self)
        self.install_systemd_service()


setup(
    name='actor',
    version=version,
    description='Actor the activity enforcer',
    long_description=open('README.md').read(),
    author='Tomas Babej',
    author_email='tomasbabej@gmail.com',
    license='AGPLv3',
    url='https://github.com/tbabej/actor',
    download_url='https://github.com/tbabej/actor/downloads',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=install_requirements,
    classifiers=[
        'Development Status :: 4 - Beta',
    ],
    entry_points={
        'console_scripts': [
            'actor = actor.core.client:main',
            'actor-daemon = actor.core.actord:main',
            'actor-debug = actor.core.actord:main_debug',
        ]
    },
    cmdclass={
        'install': InstallSystemdServiceFileInstall,
    }
)
