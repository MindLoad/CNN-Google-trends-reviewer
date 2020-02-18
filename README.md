CNN Google trends news reviewer Project
=======================================

Cloning the project repository
------------------------------

    git clone https://github.com/MindLoad/CNN-Google-trends-reviewer

Technologies/frameworks stack
-----------------------------

* Programming language - Python >= 3.8
* Web framework - Django >= 3
* DB - PostgreSQL, RabbitMQ, Redis
* async tasks - Celery, Flower

Directories structure
---------------------

    cnn/cnn          - main django project
    cnn/web          - project application
    cnn/templates    - html templates for project
    Pipfile          - required python project libraries

To work with project
----------------------------------
- Redis should be installed, as result backend for celery
- RabbitMQ should be installed, as Queue manager for celery


Start Django project for first time

```
#!bash

cd cnn
python manage.py createsuperuser

```

Start celery worker
```
#!bash

cd cnn && celery -A cnn worker -l info
```
Start celery beat
```
#!bash

cd cnn && celery -A cnn beat -l info
```
Start celery Flower
```
#!bash

cd cnn && flower -A cnn --port=5555
```
