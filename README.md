## If requirements.txt didn't install all the package required, can do it manually
` docker-compose run --rm dashboard sh -c "pip install psycopg2" `
` docker-compose run --rm dashboard sh -c "pip install gunicorn" `
` docker-compose run --rm dashboard sh -c "pip install django-heroku" `

## Make migrations
` docker-compose run --rm dashboard sh -c "python manage.py makemigrations" `

## Apply migrations to the database
` docker-compose run --rm dashboard sh -c "python manage.py migrate" `

## Create SuperUser
` docker-compose run --rm dashboard sh -c "python manage.py createsuperuser" `

## Deploy and add the app on heroku
### - Install `django-heroku`
### - Install `gunicorn`
### In `settings.py` add `import django_heroku` at the beginning of the file and `django_heroku.settings(locals())` at the end

### Create a `Procfile` at the root of the project and add the following lines
`web: gunicorn app.wsgi`

### Add remotly the project to git and setup heroku
`git init`  
`heroku create dashboardApp`
`git remote -v`
`git remote add heroku <the link outputed with 'heroku create dashboardApp'>`
`git status`
`git add .`
`git commit -m "ch(deploy)Deploy app"`
`git push heroku master>`
#### For making change to the app after deploying it with heroku
`heroku run bash`
`docker-compose run --rm dashboard sh -c "python manage.py migrate"`


## Deploy and add the app on aws
### Access to the ec2 instance created from terminal
`ssh -i "dashboardapp1.pem" ubuntu@ec2-52-90-198-62.compute-1.amazonaws.com `
`mkdir dashboard`
`exit`
### Transfer the local files to the ec2 instance inside the folder named 'dashboard'
`scp -i "dashboardapp1.pem" -r C:\Users\HP\Desktop\project\python_work\dashboard ubuntu@ec2-52-90-198-62.compute-1.amazonaws.com:/home/ubuntu/dashboard`
`ssh -i "dashboardapp1.pem" ubuntu@ec2-52-90-198-62.compute-1.amazonaws.com`
`docker-compose up`
`docker images`
`docker run -d -p 80:80 nom-de-votre-image`

### Connect to the python shell
`docker-compose run --rm dashboard sh -c "python manage.py shell"`

#### Get all users
`from django.contrib.auth import get_user_model`
`User = get_user_model()`
`users = User.objects.all()`
`print(users)`

#### Delete a user
`user = User.objects.get(username='Antman220')`
`user.delete()`

#### Delete all users
`User = get_user_model()`
`User.objects.all().delete()`

#### Exit the shell
`exit()`

### For use smtplib to automatically send email, you have to define apps passwords to your project instead of the password of your account

## Host the django app deployed with docker on heroku
- heroku login
- heroku create your-app-name
- heroku stack:set container -a your-app-name
- heroku config:set DEBUG=False ALLOWED_HOSTS="django-dashboard-docker-2d6c094b404f.herokuapp.com" -a django-dashboard-docker
- heroku config --app django-dashboard-docker
- create heroku.yml file
- heroku container:push web -a django-dashboard-docker
- heroku container:release web -a django-dashboard-docker
- after launching docker engine and build the image: heroku container:login
- heroku container:push web --app django-dashboard-docker
- docker tag heroku container:release web -a django-dashboard-docker registry.heroku.com/django-dashboard-docker/web
- docker push registry.heroku.com/django-dashboard-docker/web

## Push the project on heroku git
- git init
- heroku git:remote -a django-dashboard-docker
- git add .
- git commit -am "make it better"
- git push heroku main (or master)
- heroku git:remote -a django-dashboard-docker

## create a postgres server on amazon ec2
- ssh -i "your-key-pair.pem" ubuntu@ec2-3-93-6-22.compute-1.amazonaws.com
- sudo apt-get update -y  # For Ubuntu
- sudo apt-get install postgresql postgresql-contrib -y  # Ubuntu
- sudo service postgresql start
-  sudo -u postgres createuser dashboard_user
-  sudo -u postgres createdb dashboard_db
-  sudo -u postgres psql -c "ALTER USER dashboard_user WITH PASSWORD 'changeme';"
-  sudo vim /etc/postgresql/16/main/pg_hba.conf  # Ubuntu
-  And write: host    all             all             0.0.0.0/0               md5
-  sudo pg_ctlcluster 16 main reload
-  sudo vim /etc/postgresql/16/main/postgresql.conf  # Ubuntu
-  And write: listen_addresses = '*'
-  sudo service postgresql restart
-  add security inbounds rule for postgres app in the ec2 instance created

  ## Connect your postgres ec2 to the heroku app 
  - heroku config:set DB_HOST="ec2-3-93-6-22.compute-1.amazonaws.com" DB_NAME="dashboard_db" DB_USER="dashboard_user" DB_PASS="changeme" --app django-dashboard-docker
  - git push heroku master
  - Reconnect to the amazon ec2 instance from terminal
  - type: psql -h ec2-3-93-6-22.compute-1.amazonaws.com -U dashboard_user -d dashboard_db
  - type: GRANT ALL PRIVILEGES ON SCHEMA public TO dashboard_user;
  - GRANT ALL PRIVILEGES ON DATABASE dashboard_db TO dashboard_user;
  - heroku run python manage.py migrate --app django-dashboard-docker

    ## Verify if the django app is linked with the postgres database
    - heroku run python manage.py shell --app django-dashboard-docker
    - type this for verify
    - [
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1;")
        print(cursor.fetchone())
    - ]
    - If it return (1,), the connection with the database is successfully
    - Or type: heroku run python manage.py showmigrations --app django-dashboard-docker => for see all the migrations
