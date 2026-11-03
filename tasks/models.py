from django.db import models
from django.conf import settings

from projects.models import Label, Project


class Task(models.Model):
    project = models.ForeignKey(Project, related_name="tasks", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
        on_delete=models.SET_NULL,
    )
    labels = models.ManyToManyField(Label, blank=True, related_name="tasks")

    def __str__(self):
        return self.title
