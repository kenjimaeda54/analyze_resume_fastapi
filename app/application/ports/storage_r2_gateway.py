from abc import ABC, abstractmethod


class StorageR2GatewayInterface(ABC):

    @abstractmethod
    def upload_file(self,file_content: bytes,file_path: str) -> str:
        pass

    @abstractmethod
    def delete_file(self,file_path: str) -> None:
        pass