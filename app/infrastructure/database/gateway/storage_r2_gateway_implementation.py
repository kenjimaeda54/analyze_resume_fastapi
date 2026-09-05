import boto3

from app.application.ports.storage_r2_gateway import StorageR2GatewayInterface
from mypy_boto3_s3 import S3Client



class StorageR2GatewayImplementation(StorageR2GatewayInterface):
    def __init__(self,bucket_name: str,endpoint_url: str,access_key_id: str,secret_key:str) -> None:
        self.bucket_name = bucket_name
        self.client: S3Client = boto3.client(
            's3',
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_key,
            endpoint_url=endpoint_url
        )


    def upload_file(self,file_content: bytes,file_path: str) -> str:
        self.client.put_object(
            Bucket=self.bucket_name,
            Key=file_path,
            Body=file_content,
        )
        return f"{self.client.meta.endpoint_url}/{self.bucket_name}/{file_path}"


    def delete_file(self,file_path: str) -> None:
        self.client.delete_object(
            Bucket=self.bucket_name,
            Key=file_path
        )
