  500  git add .
  501  git commit -m 'init'
  502  git remote set-url origin https://github.com/naoshi20/django-heroku-app-1.git
  503  git push origin master
  504  python3 -m venv ./venv --prompt django-app
  505  source venv/bin/activate
  507  python -m pip install -r requirements.txt
  508  /Users/naoshi/Desktop/django-website-04/venv/bin/python -m pip install --upgrade pip
  511  python manage.py collectstatic
  512  python manage.py runserver 8001
  513  python manage.py migrate