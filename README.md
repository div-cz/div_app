git clone https://github.com/div-cz/div_app.git

sudo pip3 install virtualenvwrapper

#move this to bashrc or input it every time you will run virtualenv
export WORKON_HOME=$HOME/.virtualenvs
export PROJECT_HOME=$HOME/Devel
source /usr/local/bin/virtualenvwrapper.sh

mkvirtualenv -p python3.11 div_env

cd div_app

#This should be run on ubuntu because of package mysqlclient
apt-get install python3.11-dev default-libmysqlclient-dev build-essential

pip3 install -r requirements.txt

cd div_config

change in setting.py localhost to 127.0.0.1
DATABASE = {
   'default': {
      'HOST':'localhost'
    }	
}

docker pull mysql

docker run --name mysql-django -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE='name of DB from setting.py' -e MYSQL_USER='user from setting.py' -e MYSQL_PASSWORD='password from setting.py' -p 3306:3306 -d mysql

cd ..

python manage.py migrate

python manage.py runserver
