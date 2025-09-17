import pytest
from django.urls import reverse

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
