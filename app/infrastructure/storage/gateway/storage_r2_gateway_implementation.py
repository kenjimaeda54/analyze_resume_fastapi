import boto3
from botocore.config import Config

from app.application.ports.storage_r2_gateway import StorageR2GatewayInterface
from mypy_boto3_s3 import S3Client



class StorageR2GatewayImplementation(StorageR2GatewayInterface):
    def __init__(self,bucket_name: str,endpoint_url: str,access_key_id: str,secret_key:str) -> None:
        self.bucket_name = bucket_name
        self.client: S3Client = boto3.client(
            's3',
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_key,
            endpoint_url=endpoint_url,
            region_name='auto',  ##region auto e config para garantir corretamente a url public
            config=Config(signature_version='s3v4'),
        )


    def upload_file(self,file_content: bytes,file_path: str):
        self.client.put_object(
            Bucket=self.bucket_name,
            Key=file_path,
            Body=file_content,
        )


    def delete_file(self,file_path: str) -> None:
        self.client.delete_object(
            Bucket=self.bucket_name,
            Key=file_path
        )

    def get_download_url(self,file_path: str,expires_in: int = 1800) -> str:
        #. O que é o client_method ('get_object')?
        # O primeiro argumento passado para generate_presigned_url é o nome do método do S3 que você deseja autorizar temporariamente.
        # Como saber qual usar? O nome do método corresponde exatamente à operação do S3 que você quer realizar.
        # Se você quer baixar um arquivo: 'get_object' (equivale à API GetObject do S3).
        # Se você quer enviar/fazer upload de um arquivo: 'put_object' (equivale à API PutObject).
        # Se você quer deletar um arquivo: 'delete_object'.
        # ja que preciso baixar o arquivo, então uso get_object e no Params passo o Bucket e Key (caminho do arquivo no bucket)
        url = self.client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket_name, 'Key': file_path},
            ExpiresIn=expires_in
        )
        return url
