# Система управления заказами для кафе (Django + DRF)
---

## Основные возможности
- **CRUD для Заказов (`Order`)**
- **Расчет суммы заказа**: Автоматический подсчет через промежуточную модель `OrderItem`
- **Валидация статусов**: Контроль переходов между статусами (`pending` → `ready` → `paid`)
- **Админ-панель**: Управление Столами и Блюдами через Django Admin

---

## Быстрый старт

### 1. Клонирование и настройка
```bash
git clone https://github.com/Viktorio135/cafe_testirovanie.git
cd cafe_testirovanie
```
Далее необходимо создать файл .env, в котором записать секретный ключ: SECRET_KEY=your-secret-key
```bash
python -m venv .venv && source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Сервер доступен по адресу: http://localhost:8000

## Работа с данными
- **Таблицы Item (блюда) и Table (столы) доступны только в админке**
- **Таблица Order доступна как через веб-интерфейс, так и через админ-панель**

## Тестирование
Запуск всех тестов:
```bash
pytest
```
## REST API Endpoints

| Метод  | URL                  | Действие             |
|--------|----------------------|----------------------|
| GET    | `/api/orders/`       | Список заказов       |
| POST   | `/api/orders/`       | Создать заказ        |
| GET    | `/api/orders/{id}/`  | Детали заказа        |
| PUT    | `/api/orders/{id}/`  | Обновить заказ       |

### Пример запроса (cURL): 
```bash
curl -X POST http://localhost:8000/api/orders/ \
-H "Content-Type: application/json" \
-d '{
  "table": 1,
  "status": "pending",
  "items": [
    {"item": 1, "quantity": 2},
    {"item": 3, "quantity": 1}
  ]
}'
```

## Развертывание с помощью Nginx и Gunicorn
### 1. Установите Gunicorn
```bash
pip install gunicorn
```
### 2. Создайте сервис для Gunicorn
Создайте файл /etc/systemd/system/gunicorn.service:
```bash
[Unit]
Description=gunicorn daemon for Cafe Order System
After=network.target

[Service]
User=your_username
Group=www-data
WorkingDirectory=/var/www/cafe_testirovanie
ExecStart=/var/www/cafe_testirovanie/venv/bin/gunicorn \
    --access-logfile - \
    --workers 3 \
    --bind unix:/var/www/cafe_testirovanie/cafe.sock \
    cafe.wsgi:application

[Install]
WantedBy=multi-user.target
```

Замените:

your_username — ваш пользователь на сервере.

/var/www/cafe_testirovanie — путь к проекту.

Запустите сервис:
```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

### 3. Настройте Nginx
Создайте конфигурационный файл /etc/nginx/sites-available/cafe:
```bash
server {
    listen 80;
    server_name your_domain.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/cafe_testirovanie/cafe.sock;
    }

    location /static/ {
        alias /var/www/cafe_testirovanie/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /var/www/cafe_testirovanie/mediafiles/;
        expires 30d;
    }
}
```
Активируйте конфиг и перезагрузите Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/cafe /etc/nginx/sites-enabled/
sudo nginx -t  # Проверка конфигурации
sudo systemctl restart nginx
```
### 4. Соберите статические файлы
```bash
python manage.py collectstatic
```

Откройте в браузере: http://your_domain.com. Всё должно работать!




