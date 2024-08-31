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
- heroku config:set DEBUG=False ALLOWED_HOSTS=your-app-name.herokuapp.com SECRET_KEY=your-secret-key -a your-app-name
- create heroku.yml file
- heroku container:push web -a your-app-name
- heroku container:release web -a your-app-name
- after launching docker engine and build the image: heroku container:login
- heroku container:push web --app django-dashboard-docker
- docker tag your-app-name registry.heroku.com/django-dashboard-docker/web
- docker push registry.heroku.com/django-dashboard-docker/web
