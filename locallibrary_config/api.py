# locallibrary_config/api.py
from ninja import ModelSchema
from ninja import NinjaAPI
from ninja import Schema, Status
from chat.models import Room
from django.shortcuts import get_object_or_404
from ninja.pagination import paginate
from datetime import timedelta
from typing import Annotated
from django.db.models import Q
from django.utils import timezone
from ninja import FilterLookup, FilterSchema, Query

api = NinjaAPI()


class RoomIn(ModelSchema):
    class Meta:
        model = Room
        fields = ["name", "topic"]


class RoomOut(ModelSchema):
    class Meta:
        model = Room
        fields = ["id", "name", "topic", "created_at"]


class Conflict(Schema):
    message: str
    existing_id: int


class RoomFilter(FilterSchema):
    search: Annotated[str | None, FilterLookup("name__icontains")] = None
    topic: Annotated[str | None, FilterLookup("topic__icontains")] = None
    recent: bool | None = None

    def filter_recent(self, value: bool) -> Q:
        week_ago = timezone.now() - timedelta(days=7)
        return Q(created_at__gte=week_ago) if value else Q(created_at__lt=week_ago)


@api.get("/rooms", response=list[RoomOut])
@paginate
def list_rooms(request, filters: Query[RoomFilter]):
    return filters.filter(Room.objects.order_by("name"))



@api.get("/rooms/{room_id}", response=RoomOut)
def get_room(request, room_id: int):
    return get_object_or_404(Room, id=room_id)


@api.post("/rooms", response={201: RoomOut, 409: Conflict})
def create_room(request, payload: RoomIn):
    existing = Room.objects.filter(name=payload.name).first()
    if existing:
        return Status(409, {"message": "A room with that name already exists", "existing_id": existing.id})
    return Status(201, Room.objects.create(**payload.dict()))

# exercise fixing attempting to update a room to have a name that already exists


@api.put("/rooms/{room_id}", response={201: RoomOut, 409: Conflict})
def update_room(request, room_id: int, payload: RoomIn):
    room = get_object_or_404(Room, id=room_id)
    if room_id != Room.objects.get(name=payload.dict().get("name")).id:
        return Status(409, {"message": f"Couldn't rename '{room.name}': A room named '{payload.dict().get("name")}' already exists", "existing_id": Room.objects.get(name=payload.dict().get("name")).id})
    for attr, value in payload.dict().items():
        setattr(room, attr, value)
    room.save()
    return Status(201, room)


@api.delete("/rooms/{room_id}", response={204: None})
def delete_room(request, room_id: int):
    get_object_or_404(Room, id=room_id).delete()
