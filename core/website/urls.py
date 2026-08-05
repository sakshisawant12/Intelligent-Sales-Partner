from django.urls import path
from .views import home, get_code, embed, contact, about, features


urlpatterns = [
    path("", home, name="home"),
    path("get-code/", get_code, name="get_code"),
    path("embed/", embed, name="embed"),
    path("contact/", contact, name="contact"),
    path("about/", about, name="about"),
    path("features/", features, name="features"),
]

