from app.domain.exception.base import FieldErrors


## para funiocnar  precisa verificar o retornaor do
##er
##{'ctx': {'max_length': 11}, 'input': '3434343888888888888', 'loc': ('cpf',),
# 'msg': 'String should have at most 11 characters',
# 'type': 'string_too_long', 'url': 'https://errors.pydantic.dev/2.13/v/string_too_long'}
# repara qeu  o tipoe e string_too_long
FIELD_MESSAGES: dict = {
    "cpf": {
        "string_too_long": "CPF should have max 11 character",
    },
}


def build_field_error(error: dict) -> FieldErrors:
    #aqui vai ser uma tupla exemplo ('endereco', 'cep') ou ('cpf',) e vai ser transformado em uma string endereco.cep ou cpf
    field = ".".join(str(x) for x in error["loc"])
    field_msgs = FIELD_MESSAGES.get(field, {})
    #get retornar a mensagem a baseada no key nesse caso e o type string_too_long
    msg = field_msgs.get(error["type"], error["msg"])
    return FieldErrors(field=field, message=msg)