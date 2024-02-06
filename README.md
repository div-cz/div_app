#Steps to run app on local

#This should be run on ubuntu because of package mysqlclient
* apt-get install python3.11-dev default-libmysqlclient-dev build-essential

* git clone https://github.com/div-cz/div_app.git

* cd div_app

* rm -rf div_env

* python3.11 -m venv div_env

* source div_env/bin/activate

* pip install -r requirements.txt

* cd div_config

* change in setting.py localhost to 127.0.0.1
```
DATABASE = {
   'default': {
      'HOST':'localhost'
    }	
}
```
* docker pull mysql

* docker run --name mysql-django -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE='name of DB from setting.py' -e MYSQL_USER='user from setting.py' -e MYSQL_PASSWORD='password from setting.py' -p 3306:3306 -d mysql

* cd ..

* python manage.py migrate

* python manage.py runserver
