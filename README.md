
![Foodgram workflow](https://github.com/wertigo285/yatube/workflows/yatube/badge.svg)
# Проект "Yatube"


Учебный проект, по разработке Yatube — онлайн-сервиса для публикации дневников, пользователи которого могут подписываться на публикации понравившихся авторов.


## Установка

### 1. Установить Docker

Процесс установки описан в [официальном руководстве](https://docs.docker.com/engine/install/).

### 2. Клонировать репозиторий

```
git clone git@github.com:wertigo285/yatube.git 
```


## Запук проекта

Для запуска проекта в папке клонированного репозитория необходимо выполнить команду.

```
docker-compose up
```

После построения образов приложение Yatube будет развернуто в виде двух docker контейнеров:
* web - контейнер веб-приложения, загруженный из образа
* nginx - контейнер с веб-серером


Для начального заполнения базы тестовыми данными в корневой папке проекта необходимо выполнить команды:
```
docker exec -it web python manage.py makemigrations
docker exec -it web python manage.py migrate
docker exec -it web python manage.py collectstatic
docker exec -it web python manage.py loaddata data_dump.json
```


## Управление запущенным приложением

### Создать суперпользователя
```
docker exec -it web python manage.py createsuperuser
```

### Создать миграции
```
docker exec -it web python manage.py makemigrations
```

### Выполнить миграции
```
docker exec -it web python manage.py migrate
```

### Заполнить базу данных тестовыми данными
```
docker exec -it web python manage.py loaddata data_dump.json 
```

### Остановить проект
В командной строке, в папке репозитория выполнить:
```
docker-compose down
```
### Использованные технологии

* [Python 3.8](https://www.python.org/)
* [Django](https://www.djangoproject.com/)
* [Docker](https://www.docker.com/)
* [SQLite](https://www.sqlite.org/)
* [NGINX](https://nginx.org/)
