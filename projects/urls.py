from django.urls import path
from .views import project_list_view, project_detail_view, repository_detail_view

urlpatterns = [
    path("", project_list_view, name="project_list"),
    path("tech/<str:tech_slug>/", project_list_view, name="project_list_by_tech"),
    path("<str:project_slug>/", project_detail_view, name="project_detail"),
    path("<str:project_slug>/<str:repo_slug>/", repository_detail_view, name="repository_detail"),
]
