pip install -r config/requirements.txt
python config/manage.py collectstatic --noinput
python config/manage.py migrate