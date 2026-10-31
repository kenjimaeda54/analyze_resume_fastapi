from abc import ABC, abstractmethod


class NotificationGatewayInterface(ABC):

   @abstractmethod
   def notify_new_application(
           self,
           candidate_email: str,
           candidate_name: str,
           vacancy_title:  str,
           application_public_id: str,
           list_word_keys:  list[str],
           url_public_resume: str):
           pass
