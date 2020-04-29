  bbv# mystock

启动程序
 venv/bin/python manage.py runserver -H localhost

更新股东持股数据
 venv/bin/python update_stock_holder.py

更新财务数据
 venv/bin/python update_stock_finance.py

更新交易数据
 venv/bin/python update_stock_trade.py


生产环境的启动
 venv/bin/uwsgi --ini uwsgi.ini | tail -f uwsgi.log
 venv/bin/uwsgi --reload uwsgi.pid | tail -f uwsgi.log


发版流程
   调整version_no 为当前日期


centos:
   解决：EnvironmentError: mysql_config not found
   yum install python-devel mysql-devel


virtualenvs 配置：
 virtualenv venv

激活 virtualenvs：
 source venv/bin/activate

退出 virtualenvs：
 deactivate



安装依赖
pip install -r requirements.txt


安装
  pip install jupyter
调试工具
   jupyter notebook

Celery 启动命令
   venv/bin/celery -A mycelery:celery worker --loglevel=info --beat --logfile=./celery.beat.log

   stop:
   ps auxww | grep 'celery worker' | awk '{print $2}' | xargs kill -9
   
升级后报错No module named 'flask.ext'
    找到jinja2ext.py，将from flask.ext.cache import make_template_fragment_key改为from flask_cache import make_template_fragment_key   

生产环境调试加载数据
   from webapp import app, db, config_app, register_blueprints, celery 
   config_app(app, 'scriptfan.cfg')
   app.app_context().push()   


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