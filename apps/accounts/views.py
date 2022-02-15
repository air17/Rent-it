from datetime import timedelta
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .forms import RegistrationForm
from apps.rentitapp import models


@login_required
def profile_view(request, pk):
    """Displays a user profile, their comments and active ads."""

    user = get_object_or_404(get_user_model(), pk=pk)

    context = {"user": user}

    # Adding received comments to context
    comments = models.Comment.objects.filter(profile=user)
    context["comments"] = comments

    # Getting active ads of the user
    public_ads = models.Advertisement.objects.filter(author=user, active=True)

    # Filtering new ads for non-premium users
    if request.user.is_anonymous or not request.user.is_premium:
        public_ads = public_ads.filter(date_published__lte=timezone.now() - timedelta(days=1))

    context["public_ads"] = public_ads

    return render(request, "accounts/profile.html", context)


@login_required
def account_view(request):
    """Displays a user profile, their comments and all ads
    for an authenticated user.
    """

    user = request.user
    context = {"user": user}

    # Adding comments
    comments = models.Comment.objects.filter(profile=user)
    context["comments"] = comments

    # Adding own ads
    context["active_ads"] = models.Advertisement.objects.filter(author=user, active=True)
    context["deactivated_ads"] = models.Advertisement.objects.filter(author=user, active=False)

    return render(request, "accounts/account.html", context)


def registration_view(request):
    """Displays and processes a user registration form"""

    if not request.user.is_anonymous:
        return HttpResponseRedirect("/")
    if request.method == "POST":
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            new_user = form.save()
            login(request, user=new_user)
            return redirect("accounts:account")
    else:
        form = RegistrationForm()
    return render(request, "registration/registration.html", context={"form": form})
