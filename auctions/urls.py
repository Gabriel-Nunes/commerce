from django.urls import path

from . import views

app_name = "auctions"
urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("listing_view/<int:id>/", views.listing_view, name="listing_view"),
    path("create_listing/", views.create_listing, name="create_listing"),
    path("edit_listing/<int:id>/", views.edit_listing, name="edit_listing"),
    path("set_bid/<int:id>/", views.set_bid, name="set_bid"),
    path("close_auction/<int:id>/", views.close_auction, name="close_auction"),
    path("my_wins/", views.my_wins, name="my_wins"),
    path("comment/<int:id>", views.comment, name="comment"),
    path("watchlist/", views.watchlist, name="watchlist"),
]
