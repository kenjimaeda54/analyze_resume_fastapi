from abc import ABC, abstractmethod


class StorageR2GatewayInterface(ABC):

    @abstractmethod
    def upload_file(self,file_content: bytes,file_path: str):
        pass

    @abstractmethod
    def delete_file(self,file_path: str) -> None:
        pass

    @abstractmethod
    def get_download_url(self,file_path: str,expires_in: int = 1800) -> str:
        pass