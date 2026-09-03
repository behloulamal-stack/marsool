pip install -r config/requirements.txt
python core/manage.py collectstatic --noinput
python core/manage.py migrate