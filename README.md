## Суперпользователь для проверки:
- Логин: admin
- Пароль: admin
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
