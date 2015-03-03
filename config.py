import os

path_parts = os.path.dirname(os.path.realpath(__file__)).split('/')
PROJECT_ROOT = '/'.join(path_parts) + '/'

HOME_DIR = os.path.expanduser('~')
CONFIG_DIR = os.path.join(HOME_DIR, '.actor')
