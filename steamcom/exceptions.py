class LoginFailed(Exception):
    pass


class LoginRequired(Exception):
    pass


class SessionIsInvalid(Exception):
    pass


class ApiException(Exception):
    pass
