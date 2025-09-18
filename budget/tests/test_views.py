import pytest
from django.urls import reverse
from django.contrib.auth.models import User

# tests - views.base
@pytest.mark.django_db
def test_base_view_status_code(client):
    """
    Test that the 'base' view returns a status code 200 (OK) when accessed.
    This ensures that the view is accessible and responds correctly.
    """
    url = reverse('base')
    response = client.get(url)
    assert response.status_code == 200

@pytest.mark.django_db
def test_base_view_title(client):
    """
    Test that the 'base' view contains the correct title in the HTML response.
    This ensures that the page title is correctly set as 'Budget App'.
    """
    url = reverse('base')
    response = client.get(url)
    assert '<title>Budget App</title>' in response.content.decode()

# tests - views.user_register
@pytest.mark.django_db
def test_user_register_valid_data(client):
    """
    Test that a user can successfully register with valid data.
    This test checks if the user is redirected to the login page after a successful registration.
    """
    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password1': 'Test123!!',
        'password2': 'Test123!!',
    }

    response = client.post(reverse('register'), data)

    assert response.status_code == 302
    assert response.url == reverse('login')

@pytest.mark.django_db
def test_user_register_invalid_data(client):
    """
    Test that the registration fails when invalid data is provided.
    This test checks if the user is not redirected and if the form validation error for password mismatch appears.
    """
    url = reverse('register')
    data = {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password1': 'Test123!',
        'password2': 'password124',
    }
    response = client.post(url, data)

    assert response.status_code == 200
    assert 'password2' in response.content.decode()

# tests - views.user_login
@pytest.mark.django_db
def test_user_login_valid_data(client):
    """
    Test that a user can log in successfully with valid credentials.
    This test checks if the user is redirected to the dashboard after a successful login.
    """
    user = User.objects.create_user(username='testuser', password='testpassword')

    url = reverse('login')
    response = client.post(url, {'username': 'testuser', 'password': 'testpassword'})

    assert response.status_code == 302
    assert response.url == reverse('dashboard')

@pytest.mark.django_db
def test_user_login_invalid_data(client):
    """
    Test that login fails with invalid credentials.
    This test checks if the user sees an error message when providing incorrect login data.
    """
    url = reverse('login')
    response = client.post(url, {'username': 'wronguser', 'password': 'wrongpassword'})

    assert response.status_code == 200
    assert 'Username or password is incorrect' in response.content.decode()
