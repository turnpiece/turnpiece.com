from django.urls import path
from .views import contact_view, home_view, support_view, temphist_docs_view

urlpatterns = [
    path("", home_view, name="home"),
    path("support/", support_view, name="support"),
    path("contact/", contact_view, name="contact"),
    path("temphist/", temphist_docs_view, name="temphist_docs"),
]
