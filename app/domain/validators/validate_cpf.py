from validate_docbr import CPF


def validate_cpf(cpf: str) -> bool:
    cpf_validator = CPF()
    return cpf_validator.validate(cpf)