
from app.domain.exception.resume.resume_exception_extension_handler import ResumeInvalidExtensionException

PDF_MAGIC  = b"%PDF-"
DOCX_MAGIC = b"PK\x03\x04"
DOC_MAGIC  = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"



def validate_resume_extension(resume_bytes: bytes,content_type: str  | None) -> str:
    if content_type is None:
        raise ResumeInvalidExtensionException()

    if content_type == "application/pdf":
        if not resume_bytes.startswith(PDF_MAGIC):
            raise ResumeInvalidExtensionException()
        return "pdf"
    if content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        if not resume_bytes.startswith(DOCX_MAGIC):
            raise ResumeInvalidExtensionException()
        return "docx"
    if content_type == "application/msword":
        if not resume_bytes.startswith(DOC_MAGIC):
            raise ResumeInvalidExtensionException()
        return "doc"
    raise ResumeInvalidExtensionException()