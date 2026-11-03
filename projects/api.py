# projects/api.py
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from ninja import Router, Status

from .models import Project
from .schemas import LabelIn, LabelOut, ProjectIn, ProjectOut

router = Router(tags=["projects"])


def projects_with_counts():
    return Project.objects.annotate(
        task_count=Count("tasks"),
        unassigned_task_count=Count("tasks", filter=Q(tasks__assignee=None)),
    ).prefetch_related("labels")


@router.get("/", response=list[ProjectOut])
def list_projects(request):
    return projects_with_counts().order_by("id")


@router.post("/", response={201: ProjectOut})
def create_project(request, payload: ProjectIn):
    project = Project.objects.create(**payload.dict())
    return Status(201, projects_with_counts().get(id=project.id))


@router.get("/{project_id}", response=ProjectOut)
def get_project(request, project_id: int):
    return get_object_or_404(projects_with_counts(), id=project_id)


@router.put("/{project_id}", response=ProjectOut)
def update_project(request, project_id: int, payload: ProjectIn):
    project = get_object_or_404(projects_with_counts(), id=project_id)
    for attr, value in payload.dict().items():
        setattr(project, attr, value)
    project.save()
    return project


@router.delete("/{project_id}", response={204: None})
def delete_project(request, project_id: int):
    get_object_or_404(Project, id=project_id).delete()
    return Status(204, None)


@router.post("/{project_id}/labels", response={201: LabelOut})
def create_label(request, project_id: int, payload: LabelIn):
    project = get_object_or_404(Project, id=project_id)
    return Status(201, project.labels.create(**payload.dict()))
