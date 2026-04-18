"""
サイドバーなどのナビゲーション定義。
項目の追加・並び替えはこのファイルを編集してください。
"""

SIDEBAR_BRAND = {
    'label': '家計簿',
    'url_name': 'accounts:top',
    'match': 'top',
}

# kind: "link" | "logout"  （logout は POST のみ）
SIDEBAR_NAV_ITEMS: list[dict] = [
    {
        'kind': 'link',
        'label': '収入入力',
        'url_name': 'accounts:income',
        'match': 'income',
    },
    {
        'kind': 'link',
        'label': '支出入力',
        'url_name': 'accounts:expense',
        'match': 'expense',
    },
    {
        'kind': 'link',
        'label': '日別集計',
        'url_name': 'accounts:daily_summary',
        'match': 'daily_summary',
    },
    {
        'kind': 'link',
        'label': '月度集計',
        'url_name': 'accounts:monthly_summary',
        'match': 'monthly_summary',
    },
    {
        'kind': 'link',
        'label': '目標設定',
        'url_name': 'accounts:goal_settings',
        'match': 'goal_settings',
    },
    {
        'kind': 'link',
        'label': '日記を書く',
        'url_name': 'accounts:diary_write',
        'match': 'diary_write',
    },
    {
        'kind': 'link',
        'label': '日記を見る',
        'url_name': 'accounts:diary_browse',
        'match': 'diary_browse',
    },
    {
        'kind': 'link',
        'label': 'ユーザー設定',
        'url_name': 'accounts:settings',
        'match': 'settings',
    },
    {'kind': 'logout', 'label': 'ログアウト'},
]
