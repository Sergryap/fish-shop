## On-line магазин в виде бота Telegram

Интернет магазин создан на базе API сервиса ![Moltin](https://www.moltin.com/).

В представленной программе реализованы основные методы взаимодействия покупателя с магазином:

* просмотр списка доступных товаров
* просмотр информации о конкретном товаре
* возможность добавить товар в корзину или удалить из неё
* запрос на оплату
* добавление информации о покупателе в CMS магазина

### Из чего состоит программа

* В модуле `api_store_methods.py` реализованы функции для взаимодействия с API магазина

* В модуле `bot_tg.py` реализовано взаимодействие пользователя через интерфейс telegram с API магазина

* В модуле `logger.py` реализован класс собственного обработчика логов


### Для работы бота необходимо создать файл .env в корневой директории проекта по шаблону:

```
ACCESS_TOKEN=1
TELEGRAM_TOKEN=<Токен от бота Tg>
TELEGRAM_TOKEN_LOG=<Токен от бота Tg для отправки сообщения логгера>
CHAT_ID_LOG=<Id чата для получения сообщений логгера>
CLIENT_ID=<Уникальный идентификатор клиента API магазина>
CLIENT_SECRET=<Секретный ключ клиента API магазина>
DATABASE_PASSWORD=<Пароль доступа к базе Redis>
DATABASE_HOST=<Хост от базы Redis>
DATABASE_PORT=<Порт базы Redis>
<Важно! Пустая строка в конце файла>
```

### Порядок установки бота

1. Загрузите данные в директорию для установки:

```
git clone https://github.com/Sergryap/fish-shop.git
```
![Screenshot from 2022-12-01 20-43-34](https://user-images.githubusercontent.com/99894266/205098423-0c6f9745-be6c-4e60-8322-71b292d5c9df.png)

2. Перейдите в созданную директорию:

```
cd fish-shop
```
![Screenshot from 2022-12-01 20-44-47](https://user-images.githubusercontent.com/99894266/205098557-58566d96-f64a-47cb-87b1-f796ca478dcf.png)

3. В корневой папке проекта создайте файл .env по описанию выше:

```
nano .env
```
![Screenshot from 2022-12-01 20-47-09](https://user-images.githubusercontent.com/99894266/205098658-142d043d-af4c-4f3f-a418-33ae3045142e.png)


4. Находясь в корневой папке проекта, соберите образ, выполнив команду:

```
sudo docker build --tag fish-shop:1.0 .
```
![Screenshot from 2022-12-01 20-49-25](https://user-images.githubusercontent.com/99894266/205098769-7d2562b5-3cb8-4aec-93e3-0c6436055c44.png)

5. Запустите созданный образ:

```
sudo docker run -d --name fish-shop fish-shop:1.0
```
![Screenshot from 2022-12-01 20-50-50](https://user-images.githubusercontent.com/99894266/205098857-fe945673-459d-4a38-ac8c-36b26c9b509e.png)
