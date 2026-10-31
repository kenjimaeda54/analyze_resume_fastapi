import os
import secrets
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Header, HTTPException
from starlette import status

load_dotenv()

#O compare_digest evita ataques de tempo na comparação.
#O que o secrets.compare_digest faz
#Ele compara todos os caracteres, sempre, gastando
# o mesmo tempo independente de onde está a diferença, isso evita ataques
def verify_internal_token(authorization: Annotated[str | None, Header()] = None) -> None:
    expected = f"Bearer {os.getenv('N8N_CALLBACK_TOKEN_SECRET', '')}"
    if not authorization or not secrets.compare_digest(authorization, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")