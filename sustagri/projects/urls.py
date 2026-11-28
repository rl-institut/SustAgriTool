from django.urls import path

from .views import project_create
from .views import project_delete
from .views import project_duplicate
from .views import projects_list

app_name = "projects"

urlpatterns = [
    path("", projects_list, name="home"),
    path("projects", projects_list, name="projects_list"),
    path("<int:proj_id>", projects_list, name="projects_list"),
    # Project
    path("create", project_create, name="project_create"),
    path("duplicate/<int:proj_id>", project_duplicate, name="project_duplicate"),
    path("delete/<int:proj_id>", project_delete, name="project_delete"),
]
