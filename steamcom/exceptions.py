class InvalidCredentials(Exception):
    pass


class CaptchaRequired(Exception):
    pass


class LoginRequired(Exception):
    pass


class SessionIsInvalid(Exception):
    pass