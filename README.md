# Mental Check App
 
## Django Heroku Deploy 参考
- [本堂俊輔さんのYoutube](https://www.youtube.com/watch?v=vV_eUbaEH2A)

## 初期設定
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

## staticファイルの追加方法
1. staticフォルダ以下に該当ファイルを設置
2. python manage.py collectstatic
3. cmd + Cでrunserverを停止&再起動
4. リロード

## static files import error
STATIC_ROOT: 本番環境でのみ利用される。nginxで静的ファイルを配信したい場合など。manage.py collectstaticによって静的ファイルがここにコピーされる。
STATICFILES_DIRS: ローカルで使用。cssが存在する全てのディレクトリを指定する。{% static %}タグを使った際に見に行く先のフォルダ.collectstaticを実行した際に見に行くフォルダ
STATIC_URL: https://static.example.org/filename.extにおける、https://static.example.org 部分のURL.
heroku config:set DISABLE_COLLECTSTATIC=1
ローカルでpython manage.py collectstatic --noinput してから

## gitの運用
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

## heroku posgres連携
heroku run python manage.py createsuperuser --app graspy-1

## postgres operations
- heroku addons
- heroku pg
- heroku run python manage.py migrate check　(きちんと指定する)
- heroku run python manage.py createsuperuser
- heroku psql
- \dt; (show all tabeles)
- SELECT username, email FROM auth_user;
- \q (quit)

## maintenance
heroku maintenance:on

## database migration
- python manage.py dumpdata > dump.json (出力の全てがdump.jsonに記載されてしまうため注意。printなどで出力したものもファイルに記載されてしまう。その部分は削除してからロードする。) 
- pg_dumpall > dumpfile

## DEBUG=True時の500severerrorの対応
- htmlファイルが存在しないstaticファイルを参照しようとしている可能性がある。0からhtmlを構築した方がよい。

## Procfileでデプロイ時に自動でマイグレーションが実行されるように設定しておく
- web: gunicorn myapp.wsgi
- release: python manage.py migrate