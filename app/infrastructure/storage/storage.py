import os

from fastapi import Depends
from typing import Annotated

from app.infrastructure.database.gateway.storage_r2_gateway_implementation import StorageR2GatewayImplementation
from dotenv import load_dotenv


load_dotenv()

R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME", "")
R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY_ID", "")
R2_SECRET_KEY = os.getenv("R2_SECRET_ACCESS_KEY", "")
ENDPOINT_URL = os.getenv("R2_ENDPOINT_URL", "")

def get_storage() -> StorageR2GatewayImplementation:
    return StorageR2GatewayImplementation(
        bucket_name=R2_BUCKET_NAME,
        endpoint_url=ENDPOINT_URL,
        access_key_id=R2_ACCESS_KEY,
        secret_key=R2_SECRET_KEY,
    )


#recordando o uso do Annotated
#"Estou criando um apelido chamado depends_storage. Quando eu usar esse apelido em algum lugar,
# significa: o valor final é um StorageR2GatewayImplementation, e pra conseguir esse valor, o FastAPI deve chamar get_storage()."
depends_storage = Annotated[StorageR2GatewayImplementation, Depends(get_storage)]