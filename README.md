# house

Django 製の家計簿アプリ。収入・支出、日別／月別集計、支出予算（目標）、日記、パスワード変更まで対応。

## 技術スタック

- Python 3.13 系想定 / Django 5.1（`requirements.txt` 参照）
- SQLite（既定: `db.sqlite3`）／仮想環境は `venv/`
- 設定: `config/`、アプリ: `accounts/`（テンプレート `templates/`、スタイルは主に `accounts/static/accounts/css/auth.css`）
- 日本語・タイムゾーン Asia/Tokyo（`config/settings.py`）

## 主な機能

- トップ: 今月の収支、グラフ（Chart.js CDN）、今日の目標・今日の予定
- 収入・支出の入力、日別・月度集計、明細の編集・削除
- カテゴリ別の月間支出予算（目標設定）
- 日記（作成・カレンダーで閲覧・削除）
- 予定（作成・カレンダーで確認・削除）
- メール＋パスワードでログイン／新規登録、管理サイト `/admin/`

## セットアップと起動

```bash
cd house
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

ブラウザで http://127.0.0.1:8000/ 。管理用ユーザー: `python manage.py createsuperuser`

## 初回利用手順

1. トップページから新規登録し、メールアドレスとパスワードでログインします。
2. 収入・支出を入力し、日別・月別の集計で内容を確認します。
3. 必要に応じて目標設定、日記、予定を登録します。

## ドキュメント

- [テーブル設計・ER 図](docs/database-design.md)

## 補足

- `venv/` と `db.sqlite3` は `.gitignore` 対象。
- 本番では `SECRET_KEY`・`DEBUG`・`ALLOWED_HOSTS` を必ず見直すこと。
