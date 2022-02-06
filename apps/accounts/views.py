from datetime import timedelta
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.generic import DetailView

from apps.rentitapp import models, forms


# profile page
class UserView(DetailView):
    model = get_user_model()
    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Adding comments
        comments = models.Comment.objects.filter(profile=self.object)
        context["comments"] = comments

        # Adding active ads
        public_ads = list(models.Advertisement.objects.filter(author=self.object, active=True))

        # Removing new ads for non-premium users
        if self.request.user.is_anonymous or not self.request.user.is_premium:
            for ad in public_ads:
                if ad.date_published > timezone.now() - timedelta(days=1):
                    public_ads.remove(ad)

        context["public_ads"] = public_ads

        return context


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
