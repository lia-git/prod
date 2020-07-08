#!/bin/sh
echo "start"
. /etc/profile
cd /home/ubuntu/workspace/prod
#python3 update_tmp_degree.py
#echo 'update_tmp_degree done'
#python3 update_stock_history.py
#echo 'update_stock_history done'
#python3 update_theme_history.py
#echo 'update_theme_history done'
python3 get_super_hot.py
echo 'end'

