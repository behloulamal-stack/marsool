pip install -r core/requirements.txt
python core/manage.py collectstatic --noinput
python core/manage.py migrate