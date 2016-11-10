#!/bin/bash

sudo killall actor-daemon
sudo killall actor-debug
sudo killall actor

sudo pip uninstall actor -y
sudo rm -rf actor.egg-info/ build/ dist/
sudo python setup.py install -f
sudo rm -rf actor.egg-info/ build/ dist/

#actor-debug
