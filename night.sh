cd ~/workspace/prod/
echo 'start'
python3 theme_base.py
echo 'theme_base done'
python3 mapping.py
echo 'mapping done'
python3 stock_base.py
echo 'stocks done'
python update_tmp_degree.py
echo 'update_tmp_degree done'
python update_stock_history.py
echo 'update_stock_history done'
python update_theme_history.py
echo 'update_theme_history done'
python get_super_hot.py
echo 'end'

