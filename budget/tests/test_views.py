import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.test import Client
from budget.models import Goal, Contribution, Category, Income, Expense
from datetime import datetime

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
    User.objects.create_user(username='testuser', password='testpassword')

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


# tests - views.user_logout
@pytest.mark.django_db
def test_user_logout_redirects(client):
    """
    Test that a logged-in user is redirected to the login page upon logout.
    This test ensures that after logging out, the user is redirected to the login page.
    """
    User.objects.create_user(username='testuser', password='Test123!')

    client.login(username='testuser', password='Test123!')

    response = client.get(reverse('logout'))

    assert response.status_code == 302
    assert response.url == reverse('login')


@pytest.mark.django_db
def test_user_logout_no_user_logged_in(client):
    """
    Test that a user who is not logged in is redirected to the login page when attempting to log out.
    This test ensures that even without a logged-in user, a logout request redirects to the login page.
    """
    response = client.get(reverse('logout'))

    assert response.status_code == 302
    assert response.url == reverse('login')


# tests - views.dashboard
@pytest.mark.django_db
def test_dashboard_view_status_code(client):
    """
    Test if the dashboard page loads with status code 200.
    This test ensures that the dashboard view returns the correct status code when accessed by a logged-in user.
    """
    user = User.objects.create_user(username='testuser', password='Test123!')
    client.login(username='testuser', password='Test123!')
    url = reverse('dashboard')
    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_dashboard_view_context_data(client):
    """
    Test if the correct context data is passed to the dashboard view.
    This test checks if the user's goals, category summary, and financial data are included in the context.
    """
    user = get_user_model().objects.create_user(username="testuser", password="password")
    client = Client()
    client.login(username="testuser", password="password")

    category = Category.objects.create(name="Test Category")
    goal = Goal.objects.create(
        owner=user,
        name="Test Goal",
        target_amount=500
    )
    Contribution.objects.create(goal=goal, contributor=user, amount=100)

    last_month = datetime.now().month - 1 if datetime.now().month > 1 else 12
    Income.objects.create(user=user, category=category, amount=200, date=datetime(datetime.now().year, last_month, 1))
    Expense.objects.create(user=user, category=category, amount=100, date=datetime(datetime.now().year, last_month, 1))

    response = client.get(reverse('dashboard'))

    assert response.status_code == 200

    assert 'user_goals' in response.context
    assert len(response.context['user_goals']) == 1
    assert response.context['user_goals'][0]['goal'].name == "Test Goal"
    assert response.context['user_goals'][0]['total_contributions'] == 100
    assert response.context['user_goals'][0]['progress'] == 20.0
    assert 'category_summary' in response.context
    assert len(response.context['category_summary']) == 1
    assert response.context['category_summary'][0]['category'].name == "Test Category"
    assert response.context['category_summary'][0]['total_expenses_in_category'] == 100
    assert response.context['category_summary'][0]['total_incomes_in_category'] == 200

    assert response.context['total_expenses'] == 100
    assert response.context['total_incomes'] == 200
    assert response.context['total_balance'] == 100
