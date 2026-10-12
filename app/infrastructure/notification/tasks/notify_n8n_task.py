import os
import time

import httpx
import jwt

from dotenv import load_dotenv

load_dotenv()



webhook_url = os.getenv("N8N_WEBHOOK_URL") or ""
jwt_secret = os.getenv("N8N_JWT_SECRET")

def notify_n8n_task(
    candidate_email: str,
    candidate_name: str,
    vacancy_title: str,
    resume_path: str
):

    assert jwt_secret is not None, "JWT  is not set"

    token = jwt.encode(
        {"sub": "analyzes-resume-api", "iat": int(time.time()), "exp": int(time.time()) + 60},
        jwt_secret,
        algorithm="HS256",
    )

    response = httpx.post(
        webhook_url,
        json={
            "candidate_email": candidate_email,
            "candidate_name": candidate_name,
            "vacancy_title": vacancy_title,
            "resume_path": resume_path
        },
        headers={"Authorization": f"Bearer {token}"},
        timeout=10.0
    )
    #se der erro HTTP, o RQ entende que falhou e aplica retry
    response.raise_for_status()

