from datetime import timedelta
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils import timezone

from apps.rentitapp import models, forms


# profile page
@login_required
def profile_view(request, pk):
    user = get_user_model().objects.get(pk=pk)

    context = {"user": user}

    # Adding comments
    comments = models.Comment.objects.filter(profile=user)
    context["comments"] = comments

    # Adding active ads of the user
    public_ads = models.Advertisement.objects.filter(author=user, active=True)

    # Filtering new ads for non-premium users
    if request.user.is_anonymous or not request.user.is_premium:
        public_ads = public_ads.filter(date_published__lte=timezone.now() - timedelta(days=1))

    context["public_ads"] = public_ads

    return render(request, "accounts/profile.html", context)


# personal account page
@login_required
def account_view(request):
    template_name = "accounts/account.html"

    user = request.user

    context = {"user": user}

    # Adding comments
    comments = models.Comment.objects.filter(profile=user)
    context["comments"] = comments

    # Adding own ads
    context["active_ads"] = models.Advertisement.objects.filter(author=user, active=True)
    context["deactivated_ads"] = models.Advertisement.objects.filter(author=user, active=False)

    return render(request, template_name, context)


# user registration
def registration(request):
    if not request.user.is_anonymous:
        return HttpResponseRedirect("/")
    if request.method == "POST":
        form = forms.RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            new_user = form.save()
            login(request, user=new_user)
            return redirect("accounts:account")
    else:
        form = forms.RegistrationForm()
    return render(request, "registration/registration.html", context={"form": form})
