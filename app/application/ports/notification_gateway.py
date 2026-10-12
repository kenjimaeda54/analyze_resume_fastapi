from abc import ABC, abstractmethod


class NotificationGatewayInterface(ABC):

   @abstractmethod
   def notify_new_application(
           self,
           candidate_email: str,
           candidate_name: str,
           vacancy_title:  str,
           resume_path: str):
           pass
