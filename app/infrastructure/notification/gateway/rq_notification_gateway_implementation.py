
from rq import Queue, Retry
from app.application.ports.notification_gateway import NotificationGatewayInterface
from app.infrastructure.notification.tasks.notify_n8n_task import notify_n8n_task

class RQNotificationGatewayImplementation(
    NotificationGatewayInterface
):
    def __init__(self, queue: Queue):
        self.queue = queue

    def notify_new_application(
           self,
           candidate_email: str,
           candidate_name: str,
           vacancy_title:  str,
           list_word_keys: list[str],
           url_public_resume: str) -> None:
          self.queue.enqueue(
              notify_n8n_task,
              candidate_email = candidate_email,
              candidate_name = candidate_name,
              vacancy_title = vacancy_title,
              list_word_keys = list_word_keys,
              url_public_resume = url_public_resume,
              retry=Retry(max=3, interval=[10, 30, 60]) # aguarda 3 tentaivas primerio 10s, depois 30s, depois 60s
          )