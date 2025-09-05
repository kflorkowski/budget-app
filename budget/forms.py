from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

class UserLoginForm(AuthenticationForm):
    """
    Form used for user login, extending the default AuthenticationForm.
    It includes the username and password fields.
    """
    pass

class UserRegisterForm(UserCreationForm):
    """
    Form used for user registration, extending the default UserCreationForm.
    It includes the username, email, and password fields.
    """
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')