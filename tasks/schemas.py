from django.contrib.auth.models import User
from ninja import ModelSchema
from projects.schemas import LabelOut
from .models import Task


class UserOut(ModelSchema):
    display_name: str

    class Meta:
        model = User
        fields = ["id", "username"]

    @staticmethod
    def resolve_display_name(user):
        return user.get_full_name() or user.username
    

class TaskIn(ModelSchema):
    assignee_id: int | None = None
    label_ids: list[int] = []
    
    class Meta:
        model = Task
        fields = ["title", "description"]


class TaskOut(ModelSchema):
    assignee: UserOut | None
    labels: list[LabelOut]
    
    class Meta:
        model = Task
        fields = ["id", "project", "title", "description", "created_at"]