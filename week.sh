#!/bin/sh
echo "start"
# */9 * * * *   . /etc/profile; cd /home/ubuntu/workspace/prod  && python3 every.py
. /etc/profile
cd /data/prod
echo 'start'
python3 theme_base.py
echo 'theme_base done'
python3 mapping.py
echo 'mapping done'
python3 stock_base.py
echo 'stocks done'