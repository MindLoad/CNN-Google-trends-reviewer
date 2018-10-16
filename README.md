CNN Google trends news reviewer Project
=======================================

Cloning the project repository
------------------------------

    git clone https://github.com/MindLoad/CNN-Google-trends-reviewer

Technologies/frameworks stack
-----------------------------

* Programming language - Python 3.6.6
* Web framework - Django 2.1.2
* DB - SQlite, Redis, Celery

Directories structure
---------------------

    cnn/cnn          - main django project
    cnn/web          - project application
    cnn/templates    - html templates for project
    requirements.txt - list of required third-party Python libraries

To work with project
----------------------------------
- Redis should be installed, as broker for celery


Start Django project

```
#!bash

cd cnn
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

```

Start celery worker
```
#!bash

cd cnn
celery -A cnn worker -l info
```
Start celery beat
```
#!bash

cd cnn
celery -A cnn beat -l info
```
Start celery Flower
```
#!bash

cd cnn
flower -A cnn --port=5555
```
