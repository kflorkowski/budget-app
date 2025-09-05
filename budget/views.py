from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .forms import UserLoginForm, UserRegisterForm

# Create your views here.
def base(request):
    """Renders the 'base.html' page."""
    return render(request, 'base.html')

def user_login(request):
    """
    Handles user login.

    POST - Authenticates the user using the provided username and password.
          If the credentials are correct, logs the user in and redirects to the dashboard.
          If the credentials are incorrect, an error message is displayed.

    GET - Displays the login form for the user to input their credentials.
    """
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Username or password is incorrect')
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})


def user_register(request):
    """
    Handles user registration. If the form is submitted with valid data, a new user is created
    and redirected to the login page with a success message.

    POST - If the request method is POST, the form is processed. If the form is valid, a new user
    is created and a success message is displayed.

    GET - If the request method is GET, an empty user registration form is displayed to the user.
    """
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})
