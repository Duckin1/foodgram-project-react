# Foodrgam

 Продуктовый помощник - дипломный проект курса на Яндекс.Практикум.

 Это онлайн-сервис и API для него. 

 Здесь пользователи могут публиковать рецепты,

 Подписываться на публикации других пользователей,

 Перед походом в магазин Можно будет скачать список продуктов :grinning:

## О проекте 

- Проект завернут в Docker-контейнерах;
- Проект был развернут на сервере: <http://130.193.52.139/>
  
## Стек технологий
- Python
- Django
- Django REST Framework
- PostgreSQL
- Docker

## Зависимости
- Перечислены в файле backend/requirements.txt


## Для запуска на собственном сервере

1. Установите на сервере `docker` и `docker-compose`
2. Создайте файл `/infra/.env` Шаблон для заполнения файла нахоится в `/infra/.env.example`
3. Из директории `/infra/` выполните команду `docker-compose up -d --build`
5. Выполните миграции `sudo docker exec -it infra-web-1 python manage.py makemigrations`
6. Выполните миграции `sudo docker exec -it infra-web-1 python manage.py migrate`
6. Создайте Администратора `sudo docker exec -it infra-web-1 python manage.py createsuperuser`
7. Соберите статику `sudo docker exec -it infra-web-1 python manage.py collectstatic --no-input`
8. Из директории `/backend/` Загрузите фикстуры в Базу 

    `sudo docker exec -it infra-web-1 python manage.py loaddata fixtures.json`
8. Документация к API находится по адресу: <http://130.193.52.139/api/docs/>.

## Автор

- [Алмаз Миннибаев](https://github.com/Duckin1) 