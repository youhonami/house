from django import template

from accounts.navigation import SIDEBAR_BRAND, SIDEBAR_NAV_ITEMS

register = template.Library()


@register.inclusion_tag('accounts/partials/app_sidebar.html', takes_context=True)
def render_sidebar(context):
    """サイドバー（`navigation.py` の定義 + 現在URLによる表示状態）。"""
    request = context['request']
    n = ''
    if getattr(request, 'resolver_match', None) and request.resolver_match:
        n = request.resolver_match.url_name or ''
    return {
        'sidebar_brand': SIDEBAR_BRAND,
        'sidebar_nav_items': SIDEBAR_NAV_ITEMS,
        'n': n,
    }
