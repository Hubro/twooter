
from tortoise import fields, Tortoise
from tortoise.models import Model

from .config import settings


async def init():
    await Tortoise.init(
        db_url=settings.db_url,
        modules={
            "twooter": ["twooter.db"]
        }
    )

    await Tortoise.generate_schemas()


async def teardown():
    await Tortoise.close_connections()


class Message(Model):
    id = fields.IntField(pk=True)
    text = fields.TextField()
    tag = fields.CharField(max_length=255)
    timestamp = fields.DatetimeField(auto_now_add=True)
