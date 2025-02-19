release: python manage.py migrate
web: daphne argon_company.asgi:application --port $PORT --bind 0.0.0.0 -v2