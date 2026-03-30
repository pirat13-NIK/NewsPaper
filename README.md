## Суперпользователь для проверки:
- Логин: admin
- Пароль: admin

## Настройка email уведомлений

Для разработки письма выводятся в консоль (настройка по умолчанию).

Для реальной отправки писем:
1. Раскомментируйте SMTP настройки в `settings.py`
2. Укажите параметры вашего SMTP сервера
3. Для production рекомендуется использовать переменные окружения

## 🔐 Настройка Yandex OAuth
### Для работы входа через Яндекс необходимо:

1. Зарегистрировать приложение на https://oauth.yandex.ru/
2. Получить Client ID и Client secret
3. Вставить их в файл `NewsPaper/settings.py`:
```python
SOCIALACCOUNT_PROVIDERS = {
    'yandex': {
        'APP': {
            'client_id': 'ВАШ_CLIENT_ID',
            'secret': 'ВАШ_CLIENT_SECRET',
            'key': ''
}
