from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import UserLoginForm, UserRegisterForm, IncomeForm, ExpenseForm
from django.views.generic import TemplateView
from django.db.models import Sum
from datetime import datetime
from django.contrib.auth.decorators import login_required
from .models import Income, Expense, Goal, Contribution, Category

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

def user_logout(request):
    """
    Logs out the currently authenticated user and redirects to the login page.

    POST - Performs the logout action and redirects the user to the login page.
    """
    logout(request)
    return redirect('login')

class DashboardView(TemplateView):
    """
    Renders the dashboard page, displaying information such as user goals, contributions,
    and financial summaries by category for the previous month.

    GET - Retrieves the user's dashboard with details including:
        - User's goals with progress (total contributions vs target amount)
        - User's contributions to goals and contributions from others
        - Monthly expenses and incomes for each category
        - Total expenses, incomes, and balance for the previous month

    Context data:
        - 'user_goals': List of goals with progress details
        - 'user_contribution': Contributions made by the logged-in user
        - 'other_contribution': Contributions made by others for the user's goals
        - 'category_summary': Financial summary for each category (expenses and incomes)
        - 'total_expenses': Total expenses for the user in the previous month
        - 'total_incomes': Total income for the user in the previous month
        - 'total_balance': The balance (income - expenses) for the user in the previous month
    """
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_goals = Goal.objects.filter(owner=self.request.user)
        goals_with_progress = []
        for goal in user_goals:
            total_contributions = Contribution.objects.filter(goal=goal).aggregate(total=Sum('amount'))['total'] or 0
            progress = (total_contributions / goal.target_amount) * 100 if goal.target_amount > 0 else 0
            goals_with_progress.append({
                'goal': goal,
                'total_contributions': total_contributions,
                'progress': progress,
            })

        user_contribution = Contribution.objects.filter(contributor=self.request.user)
        other_contribution = Contribution.objects.exclude(contributor=self.request.user).filter(goal__in=user_goals)

        last_month = datetime.now().month - 1 if datetime.now().month > 1 else 12
        category_summary = []

        total_expenses = 0
        total_incomes = 0

        for category in Category.objects.all():
            category_expenses = Expense.objects.filter(category=category, user=self.request.user,
                                                       date__month=last_month)
            category_incomes = Income.objects.filter(category=category, user=self.request.user, date__month=last_month)

            total_expenses_in_category = category_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
            total_incomes_in_category = category_incomes.aggregate(Sum('amount'))['amount__sum'] or 0

            category_summary.append({
                'category': category,
                'total_expenses_in_category': total_expenses_in_category,
                'total_incomes_in_category': total_incomes_in_category,
            })

            total_expenses += total_expenses_in_category
            total_incomes += total_incomes_in_category

        total_balance = total_incomes - total_expenses

        context.update({
            'user_goals': goals_with_progress,
            'user_contribution': user_contribution,
            'other_contribution': other_contribution,
            'category_summary': category_summary,
            'total_expenses': total_expenses,
            'total_incomes': total_incomes,
            'total_balance': total_balance,
        })
        return context


@login_required
def transactions(request):
    """
    This view is responsible for displaying the user's transactions, including both expenses and incomes.

    Decorator:
    - @login_required: This decorator ensures that only authenticated users can access this view.
      If the user is not logged in, they will be redirected to the login page.

    - Retrieves the expenses and incomes associated with the authenticated user from the database.
    - Filters the `Expense` and `Income` models based on the currently logged-in user (`request.user`).
    - Renders the `transactions.html` template, passing the filtered `expenses` and `incomes` as context to the template.
    """
    expenses = Expense.objects.filter(user=request.user)
    incomes = Income.objects.filter(user=request.user)
    return render(request, 'transactions.html', {'expenses': expenses, 'incomes': incomes})


@login_required
def add_income(request):
    """
    Handles the creation of a new income entry.

    Decorator:
    - @login_required: This decorator ensures that only authenticated users can access this view.
      If the user is not logged in, they will be redirected to the login page.

    POST:
    - Processes the submitted form data to create a new income record.
    - The income is saved to the database with the current user assigned to the `user` field.
    - After successfully saving, the user is redirected to the 'transactions' page.

    GET:
    - Initializes an empty form for creating a new income record.
    - Renders the form to the user in the 'add_income' template.
    """

    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income = form.save()
            return redirect('transactions')
    else:
        form = IncomeForm()
    return render(request, 'add_income.html', {'form': form})


@login_required
def add_expense(request):
    """
    View to handle the creation of a new expense.

    Decorator:
    - @login_required: This decorator ensures that only authenticated users can access this view.
      If the user is not logged in, they will be redirected to the login page.

    POST:
    - Processes the form data, creates a new expense linked to the user, and saves it to the database.
    - After successful submission, redirects to the transactions page.

    GET:
    - Initializes an empty form for creating a new expense and renders the page.
    """
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense = form.save()
            return redirect('transactions')
    else:
        form = ExpenseForm()
    return render(request, 'add_expense.html', {'form': form})