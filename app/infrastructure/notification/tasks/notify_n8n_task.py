import os
import time

import httpx
import jwt

from dotenv import load_dotenv

load_dotenv()


def notify_n8n_task(
    candidate_email: str,
    candidate_name: str,
    vacancy_title: str,
    url_public_resume: str,
    application_public_id: str,
    list_word_keys: list[str]
):
    webhook_url = os.getenv("N8N_WEBHOOK_URL")
    jwt_secret = os.getenv("N8N_JWT_SECRET")

    if not webhook_url or not jwt_secret:
        raise RuntimeError("Missing N8N_WEBHOOK_URL and N8N_JWT_SECRET ")

    token = jwt.encode(
        {"sub": "analyzes-resume-api", "iat": int(time.time()), "exp": int(time.time()) + 60},
        jwt_secret,
        algorithm="HS256",
    )

    response = httpx.post(
        webhook_url,
        json={
            "application_public_id": application_public_id,
            "candidate_email": candidate_email,
            "candidate_name": candidate_name,
            "vacancy_title": vacancy_title,
            "url_public_resume": url_public_resume,
            "list_word_keys": list_word_keys
        },
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0
    )
    #se der erro HTTP, o RQ entende que falhou e aplica retry
    response.raise_for_status()

