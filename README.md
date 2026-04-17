# house

Django 製の家計簿アプリです。収入・支出の登録、日別／月度の集計、カテゴリ別支出予算（目標）、ユーザー設定（パスワード変更）まで一通り利用できます。

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

### ロケール・認証まわり（`config/settings.py`）

- `LANGUAGE_CODE`: `ja` / `TIME_ZONE`: `Asia/Tokyo`
- `INSTALLED_APPS`: `django.contrib.humanize` を含む（数値の桁区切り表示など）
- `TEMPLATES["DIRS"]`: プロジェクト直下の `templates/`
- `LOGIN_URL`: `accounts:login` / `LOGIN_REDIRECT_URL`: `/` / `LOGOUT_REDIRECT_URL`: `/login/`
- 静的ファイル: `STATIC_URL` = `static/`（スタイルは主に `accounts/static/accounts/css/auth.css`）

### アプリ構成（`accounts`）

| 項目 | 内容 |
|------|------|
| モデル | `IncomeEntry`（収入）、`ExpenseEntry`（支出）、`ExpenseBudget`（カテゴリ別の月間支出予算） |
| 認証 | メールアドレス + パスワードでログイン（`User.email` でユーザーを特定）。新規登録あり。登録時パスワードは **英字（a–z, A–Z）のみ・5 文字以上**（`accounts/forms.py` の `RegisterForm`） |
| ログイン後 UI | `templates/accounts/base_app.html` … ドロワー式サイドバー + メイン。メニューは **`{% render_sidebar %}`**（`accounts/templatetags/navigation_tags.py`） |
| メニュー定義 | `accounts/navigation.py` の `SIDEBAR_BRAND` / `SIDEBAR_NAV_ITEMS` |
| ログイン・登録 | `templates/accounts/base_auth.html` ベースのカード UI |
| スタイル | `accounts/static/accounts/css/auth.css` |

### 主な画面・機能

| 画面 | 説明 |
|------|------|
| **トップ**（`/`） | 今月の収入・支出合計・収支。**Chart.js**（CDN）による収入／支出の比較グラフ（`accounts/static/accounts/js/top-chart.js`） |
| **収入入力**（`/income/`） | `IncomeEntry` の登録。月別サマリへの導線あり |
| **支出入力**（`/expense/`） | `ExpenseEntry` の登録（カテゴリは `ExpenseBudget.Category` に準拠） |
| **日別集計**（`/summary/daily/`） | 日付指定・前日／翌日移動。当日の収入・支出明細、**カテゴリー別支出**、明細の編集／削除モーダル（`monthly-entry-edit.js`） |
| **月度集計**（`/summary/monthly/`） | 月指定。収支サマリ、**支出予算との比較**（目標設定がある場合）、収入・支出明細、編集／削除モーダル |
| **目標設定**（`/goals/`） | カテゴリ別の月間支出予算（`ExpenseBudget`）の入力・保存 |
| **ユーザー設定**（`/settings/`） | ログイン中ユーザーのパスワード変更 |
| **管理サイト**（`/admin/`） | Django admin |

月度・日別の明細編集は、次の API 風エンドポイントに **GET（JSON）/ POST（更新）/ DELETE（削除）** でアクセスします（`monthly-entry-edit.js` から利用）。

- `summary/entry/income/<pk>/` … `accounts:monthly_income_entry`
- `summary/entry/expense/<pk>/` … `accounts:monthly_expense_entry`

### 主要 URL（ルート直下）

`config/urls.py` で `path('', include('accounts.urls'))` しているため、次のパスがそのまま使えます。

| URL | 説明 |
|-----|------|
| `/` | トップ（要ログイン） |
| `/login/` / `/register/` | ログイン・新規登録 |
| `/logout/` | ログアウト（POST） |
| `/income/` | 収入入力 |
| `/expense/` | 支出入力 |
| `/summary/daily/` | 日別集計 |
| `/summary/monthly/` | 月度集計 |
| `/summary/entry/income/<pk>/` | 収入明細の取得・更新・削除（JSON / 要ログイン・本人のみ） |
| `/summary/entry/expense/<pk>/` | 支出明細の取得・更新・削除（同上） |
| `/goals/` | 目標設定（支出予算） |
| `/settings/` | ユーザー設定 |
| `/admin/` | 管理サイト |

### 静的ファイル（JavaScript）

| パス | 用途 |
|------|------|
| `accounts/static/accounts/js/app-nav.js` | アプリシェルのサイドバー開閉 |
| `accounts/static/accounts/js/monthly-entry-edit.js` | 月度／日別の明細モーダル（編集・削除） |
| `accounts/static/accounts/js/top-chart.js` | トップのグラフ初期化 |

トップのグラフは **Chart.js 4.4.1** を jsDelivr CDN から読み込みます。オフラインではグラフのみ表示されず、数値の表はそのまま利用できます。

## セットアップ

```bash
cd house
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
```

（任意）スーパーユーザ作成: `python manage.py createsuperuser`

## 開発サーバの起動

```bash
source venv/bin/activate
python manage.py runserver
```

ブラウザで http://127.0.0.1:8000/ を開きます。

## 補足

- `venv/` と `db.sqlite3` は `.gitignore` で除外済みです。
- 本番運用時は `SECRET_KEY`・`DEBUG`・`ALLOWED_HOSTS` を必ず見直してください。
- 本番では Chart.js を CDN ではなく自ホストの静的ファイルに置く選択も検討してください。
