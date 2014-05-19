import os

path_parts = os.path.dirname(os.path.realpath(__file__)).split('/')
PROJECT_ROOT = '/'.join(path_parts) + '/'

CONFIG_DIR = PROJECT_ROOT + 'config'
HOME_DIR = os.path.expanduser('~')
