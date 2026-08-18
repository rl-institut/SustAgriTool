from django.urls import path, re_path
from .views import *

app_name = "projects"

urlpatterns = [
    # path("", home, name="home"),
    # Project
    path("list/", projects_list, name="projects_list"),
    path("project/create/", project_create, name="project_create"),
    ]
