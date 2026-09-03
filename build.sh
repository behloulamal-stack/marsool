pip install -r requirements.txt
python core/manage.py collectstatic --noinput
python manage.py migrate