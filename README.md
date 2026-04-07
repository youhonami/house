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

### ロケール・認証まわりの設定（`config/settings.py`）

- `LANGUAGE_CODE`: `ja` / `TIME_ZONE`: `Asia/Tokyo`
- `TEMPLATES["DIRS"]`: プロジェクト直下の `templates/`
- `LOGIN_URL`: `accounts:login` / `LOGIN_REDIRECT_URL`: `/` / `LOGOUT_REDIRECT_URL`: `/login/`
- 静的ファイル URL プレフィックス: `STATIC_URL` = `static/`（CSS は `accounts/static/accounts/css/auth.css`）

### 現状のアプリ構成（開発中の機能）

| 項目 | 内容 |
|------|------|
| アプリ | **`accounts`** のみ（画面・認証・ナビ定義を集約） |
| 認証 | メールアドレス + パスワードでログイン（DB の `User.email` でユーザーを特定）。新規登録あり。登録時のパスワードは **英字（a–z, A–Z）のみ・5 文字以上**（`accounts/forms.py` の `RegisterForm`） |
| ログイン後レイアウト | `templates/accounts/base_app.html` … 左サイドバー + メイン。サイドバーは **`{% render_sidebar %}`**（`accounts/templatetags/navigation_tags.py` の inclusion タグ） |
| メニュー定義 | `accounts/navigation.py` の `SIDEBAR_BRAND` / `SIDEBAR_NAV_ITEMS` を編集（項目の追加・並び替え） |
| ログイン・登録画面 | `templates/accounts/base_auth.html` をベースにグラデ背景 + カード UI |
| スタイル | `accounts/static/accounts/css/auth.css`（認証画面 + アプリシェル + サイドバー） |
| 未実装の画面 | 収入・支出・集計・目標・設定などは **プレースホルダ**（`placeholder.html`）。トップは仮の本文のみ |

### 主要 URL（`accounts` / ルートマウント）

`config/urls.py` で `path('', include('accounts.urls'))` のため、次のパスがルート直下になります。

| URL | 説明 |
|-----|------|
| `/` | トップ（要ログイン） |
| `/login/` / `/register/` | ログイン・新規登録 |
| `/logout/` | ログアウト（POST） |
| `/income/` `/expense/` | 収入・支出（仮） |
| `/summary/daily/` `/summary/monthly/` | 日別・月度集計（仮） |
| `/goals/` | 目標設定（仮） |
| `/settings/` | ユーザー設定（仮） |

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
