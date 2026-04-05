# house

Django を使ったプロジェクトです。

## 現状の環境

| 項目 | 内容 |
|------|------|
| 言語 | Python 3.13 系（例: 3.13.1） |
| フレームワーク | Django **5.1.15** |
| プロジェクト設定パッケージ | `config`（ルートに `manage.py`） |
| データベース | SQLite（既定。`db.sqlite3`） |
| 仮想環境 | `venv/`（プロジェクト直下） |
| コンテナ | 未使用（ローカル `venv` のみ） |

### 依存パッケージ（`requirements.txt`）

- `Django==5.1.15`
- `asgiref==3.11.1`
- `sqlparse==0.5.5`

## セットアップ

```bash
cd house
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
```

## 開発サーバの起動

```bash
source venv/bin/activate
python manage.py runserver
```

ブラウザで http://127.0.0.1:8000/ を開きます。

## 補足

- `venv/` と `db.sqlite3` は `.gitignore` で除外済みです。
- 本番運用時は `SECRET_KEY`・`DEBUG`・`ALLOWED_HOSTS` を必ず見直してください。
