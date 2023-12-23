class NoobException(Exception):
    pass


class ButtonColourNotFound(NoobException):
    pass


class MemberOrGuildNotFound(NoobException):
    pass


class NoContextOrInteractionFound(NoobException):
    pass
