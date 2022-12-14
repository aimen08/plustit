from django.urls import re_path

from .views import TokensView, TokenView

app_name = "baserow.contrib.database.api.tokens"

urlpatterns = [
    re_path(r"(?P<token_id>[0-9]+)/$", TokenView.as_view(), name="item"),
    re_path(r"$", TokensView.as_view(), name="list"),
]
