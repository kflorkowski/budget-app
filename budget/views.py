from django.shortcuts import render

# Create your views here.
def base(request):
    """Renders the 'base.html' page."""
    return render(request, 'base.html')