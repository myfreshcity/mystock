# mystock

启动程序
 venv/bin/python manage.py runserver -H localhost

更新股东持股数据
 venv/bin/python refresh_stock_holder.py

更新财务数据
 venv/bin/python refresh_stock_finance.py

更新交易数据
 venv/bin/python refresh_stock_trade.py


生产环境的启动
 venv/bin/uwsgi --ini uwsgi.ini | tail -f uwsgi.log

 程序终止：
 kill -HUP `cat uwsgi.pid`
 venv/bin/uwsgi --reload uwsgi.pid | tail -f uwsgi.log

centos:
   解决：EnvironmentError: mysql_config not found
   yum install python-devel mysql-devel


virtualenvs 配置：
 virtualenv venv

激活 virtualenvs：
 source venv/bin/activate

退出 virtualenvs：
 deactivate


环境安装：
   pip install flask
   #pip install mysql-connector-python
   export PATH=$PATH:/usr/local/mysql/bin
   pip install MySQL-python 

安装依赖
pip install -r requirements.txt


安装
  pip install jupyter
调试工具
   jupyter notebook


文档参考：

virtualenvs

http://docs.python-guide.org/en/latest/dev/virtualenvs/

flask 最佳实践

https://spacewander.github.io/explore-flask-zh/1-introduction.html

http://flask.pocoo.org/docs/0.10/tutorial/

pandas
http://pandas.pydata.org/pandas-docs/stable/index.html 

SQLAlchemy
https://muxuezi.github.io/posts/sqlalchemy-introduce.html

nvd3
http://nvd3.org/examples/index.html

datatables
https://datatables.net/manual/

d3
https://github.com/mbostock/d3/wiki/API-Reference

http://v4.bootcss.com/examples/dashboard/

highcharts

http://www.hcharts.cn/demo/highcharts.php

bootstrap
http://www.runoob.com/bootstrap/bootstrap-tutorial.html