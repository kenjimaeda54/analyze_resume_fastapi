
from app.domain.exception.resume.resume_exception_extension_handler import ResumeInvalidExtensionException

PDF_MAGIC  = b"%PDF-"
DOCX_MAGIC = b"PK\x03\x04"



def validate_resume_extension(resume_bytes: bytes,content_type: str  | None) -> str:
    if content_type is None:
        raise ResumeInvalidExtensionException()

    if content_type == "application/pdf":
        if not resume_bytes.startswith(PDF_MAGIC):
            raise ResumeInvalidExtensionException()
        return "pdf"
    if content_type in {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
    }:
        if not resume_bytes.startswith(DOCX_MAGIC):
            raise ResumeInvalidExtensionException()
        return "docx"
    raise ResumeInvalidExtensionException()