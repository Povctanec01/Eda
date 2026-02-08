0.Предисловие
Ссылка на видеоролик: https://rutube.ru/video/private/d0d67f2fc6baf9bd8b59645da18e8781/?p=VDx28HC4UEfDvbxOklD2pQ
Наш проект — это современная система управления школьной столовой, 
разработанная для Московской предпрофессиональной олимпиады.

Краткое описание:
Мы создали веб-приложение, которое полностью автоматизирует процесс питания в школе. 
Оно заменяет устаревшие бумажные журналы и талоны, делая питание удобным, прозрачным и безопасным для всех.
Мы построили систему на надёжной и бесплатной основе (Python/Django + PostgreSQL), что делает её доступной для любой школы. 
Она безопасна, масштабируема и проста в использовании.
В итоге, наша система экономит время, снижает затраты, повышает безопасность питания и делает школьную столовую по-настоящему современной и удобной для всех.

Полезные команды:
-Удаление контейнера: docker-compose down -v
-Очистка всего скаченного: docker system prune -a -f
-Создание контейнера: docker-compose down build
-Включение контейнера: docker-compose down up

1.Начало
wsl --update
wsl --install
wsl
sudo su


2.Развёртываение контейнера
!!!ВАЖНО!!!
----Settings → Resources → WSL Integration
----Убедитесь, что ваш дистрибутив включен

mkdir ./Project
sudo chmod 777 ./Project
cd ./Project
git clone https://github.com/Povctanec01/Eda.git django-project
cd django-project
docker-compose build
docker-compose up -d


3.Создание админа
docker exec -it django_web python manage.py createsuperuser
docker exec -it django_web bash

!!Вставьте код ниже целиком и нажмите Enter!!
python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
from main.models import Profile
User = get_user_model()
user = User.objects.get(username='admin')
profile, created = Profile.objects.get_or_create(user=user)
profile.role = 'admin'
profile.save()
print(f"Роль 'admin' присвоена пользователю {user.username}")
EOF

Ctrl + D для выхода
