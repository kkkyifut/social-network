# social-network
### Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/kkkyifut/social-network.git
```
```
cd social-network
```

Cоздать и активировать виртуальное окружение:
```
python3 -m venv env
```
```
source env/bin/activate
venv\scripts\activate (windows)
```

Установить зависимости из файла requirements.txt:
```
python3 -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```

Выполнить миграции:
```
python3 manage.py migrate
```

Запустить проект:
```
python3 manage.py runserver
```
