#!/bin/sh
. /etc/profile
. ~/.bash_profile
cd /home/yqp/ExerciseCode/myproject/novelcrawler
source bin/activate
python novelcrawler.py
deactivate
cd ~
