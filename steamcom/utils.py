from steamcom.exceptions import LoginRequired


def login_required(func):
    def func_wrapper(self, *args, **kwargs):
        if self.was_login_executed == False:
            raise LoginRequired('Use LoginExecutor.login method first')
        else:
            return func(self, *args, **kwargs)
    return func_wrapper
