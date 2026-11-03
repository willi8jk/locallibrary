from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from ninja import PatchDict, Path, Router, Status
from ninja.errors import HttpError

from projects.models import Project

from .models import ALLOWED_TRANSITIONS, Priority, Task
from .schemas import StatusIn, TaskIn, TaskOut, TaskUpdate

router = Router(tags=["tasks"])


def check_relations(project, payload):
    if payload.assignee_id is not None and not User.objects.filter(id=payload.assignee_id).exists():
        raise HttpError(400, f"User {payload.assignee_id} does not exist")
    labels = list(project.labels.filter(id__in=payload.label_ids))
    if len(labels) != len(set(payload.label_ids)):
        raise HttpError(400, "Unknown label id for this project")
    return labels


@router.get("/", response=list[TaskOut])
def list_tasks(request, project_id: Path[int]):
    project = get_object_or_404(Project, id=project_id)
    return project.tasks.select_related("assignee").prefetch_related("labels").order_by("id")


@router.post("/", response={201: TaskOut})
def create_task(request, project_id: Path[int], payload: TaskIn):
    project = get_object_or_404(Project, id=project_id)
    labels = check_relations(project, payload)
    task = Task.objects.create(project=project, **payload.dict(exclude={"label_ids"}))
    task.labels.set(labels)
    return Status(201, task)


@router.get("/{task_id}", response=TaskOut)
def get_task(request, project_id: Path[int], task_id: int):
    return get_object_or_404(Task, id=task_id, project_id=project_id)


@router.patch("/{task_id}", response=TaskOut)
def update_task(request, project_id: Path[int], task_id: int, payload: PatchDict[TaskUpdate]):
    task = get_object_or_404(Task, id=task_id, project_id=project_id)
    for attr, value in payload.items():
        setattr(task, attr, value)
    if task.priority == Priority.URGENT and task.due_date is None:
        raise HttpError(400, "Urgent tasks need a due date")
    task.save()
    return task


@router.post("/{task_id}/status", response=TaskOut)
def change_status(request, project_id: Path[int], task_id: int, payload: StatusIn):
    task = get_object_or_404(Task, id=task_id, project_id=project_id)
    if payload.status not in ALLOWED_TRANSITIONS[task.status]:
        raise HttpError(409, f"Can't move a task from {task.status} to {payload.status}")
    task.status = payload.status
    task.save()
    return task