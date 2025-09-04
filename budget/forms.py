from django.contrib.auth.forms import AuthenticationForm

class UserLoginForm(AuthenticationForm):
    """
    Form used for user login, extending the default AuthenticationForm.
    It includes the username and password fields.
    """
    pass