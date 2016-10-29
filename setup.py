from setuptools import setup, find_packages

install_requirements = ['psutil']

version = '0.8.0'

try:
    import importlib
except ImportError:
    install_requirements.append('importlib')

setup(
    name='actor',
    version=version,
    description='Actor the activity enforcer',
    long_description=open('README.md').read(),
    author='Tomas Babej',
    author_email='tomasbabej@gmail.com',
    license='MIT',
    url='https://github.com/tbabej/actor',
    download_url='https://github.com/tbabej/actor/downloads',
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requirements,
    classifiers=[
        'Development Status :: 4 - Beta',
    ],
    entry_points={
        'console_scripts': [
            'actor = actor.core.client:main',
            'actor-daemon = actor.core.actord:main',
            'actor-debug = actor.core.main:debug_main',
        ]
    }
)
