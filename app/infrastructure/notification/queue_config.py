import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends
from redis import Redis
from rq import Queue

from app.infrastructure.notification.gateway.rq_notification_gateway_implementation import RQNotificationGatewayImplementation

load_dotenv()


redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')


redis_connection = Redis.from_url(redis_url)
notification_queue = Queue("notifications",connection=redis_connection)

def get_notification_gateway() -> RQNotificationGatewayImplementation:
    return RQNotificationGatewayImplementation(queue=notification_queue)


depends_notification_gateway = Annotated[RQNotificationGatewayImplementation, Depends(get_notification_gateway)]