# Django Heroku Deploy 参考
- [本堂俊輔さんのYoutube](https://www.youtube.com/watch?v=vV_eUbaEH2A)

# 初期設定
1. git add .
2. git commit -m 'init'
3. git remote set-url origin https://github.com/naoshi20/django-heroku-app-1.git
4. git push origin master
5. python3 -m venv ./venv --prompt django-app
6. source venv/bin/activate
7. python -m pip install -r requirements.txt
8. /Users/naoshi/Desktop/mentalcheck2/venv/bin/python -m pip install --upgrade pip
9. python manage.py collectstatic
10. python manage.py runserver 8001
11. python manage.py migrate

# Staticファイルの追加方法
1. staticフォルダ以下に該当ファイルを設置
2. python manage.py collectstatic
3. cmd + Cでrunserverを停止&再起動
4. リロード

# gitの運用
1. git clone
2. git branch dev
3. git checkout dev
4. 開発
5. git add, commit
6. git push origin dev
7. プルリク作成
8. マージ
9. git checkout master #masterを最新化したい
10. git pull #最新状態を取り込める

# heroku posgres連携
heroku run python manage.py createsuperuser --app graspy-1