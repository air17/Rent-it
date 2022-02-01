from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import ListView

from . import models, forms


# main page
class IndexView(ListView):
    model = models.Advertisement

    # changing default context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # sorting
        sort_by = self.request.GET.get("sort")
        if sort_by:
            if sort_by in ["name", "date_published", "price"]:
                context["advertisement_list"] = context["advertisement_list"].order_by(sort_by)
                context["sort"] = sort_by
                if self.request.GET.get("desc"):
                    context["advertisement_list"] = context["advertisement_list"].reverse()
                    context["sort"] += "_d"

        # filtering categories
        category = self.request.GET.get("category")
        if category:
            context["category"] = category
            if category == "flat":
                context["advertisement_list"] = context["advertisement_list"].filter(
                    category=models.Advertisement.FlatCategory.FLAT)
            elif category == "house":
                context["advertisement_list"] = context["advertisement_list"].filter(
                    category=models.Advertisement.FlatCategory.HOUSE)
            elif category == "room":
                context["advertisement_list"] = context["advertisement_list"].filter(
                    category=models.Advertisement.FlatCategory.ROOM)

        # making a list to be able to remove items
        context["advertisement_list"] = list(context["advertisement_list"])

        # removing non-active ads
        context["advertisement_list"] = list(filter(lambda ad: ad.active,
                                                    context["advertisement_list"]))

        # removing new ads for non-premium
        if self.request.user.is_anonymous or not self.request.user.is_premium:
            context["advertisement_list"] = list(filter(lambda ad:
                                                        ad.date_published < timezone.now() - timedelta(days=1),
                                                        context["advertisement_list"]))

        return context


# advertisement details page
def advertisement_view(request, pk=None):
    ad = models.Advertisement.objects.get(pk=pk)

    # Redirect if ad is new and user is not premium
    if request.user != ad.author and \
            (request.user.is_anonymous or not request.user.is_premium) and \
            ad.date_published > timezone.now() - timedelta(days=1):
        return HttpResponseRedirect("/")

    # Setting context, adding category label, adding default variables
    context = {"advertisement": ad,
               "category": ad.FlatCategory(ad.category).label,
               "just_added": False,
               "comment_added": False}

    # Showing notification when added or edited
    if request.GET.get("success") or request.GET.get("edited"):
        context["just_added"] = True
        context["status_text"] = "Объявление успешно размещено!"
        if request.GET.get("edited"):
            context["status_text"] = "Объявление отредактировано"

    # Comments form
    context["new_comment"] = forms.NewComment()

    # Processing comment
    if request.GET.get("comment") and request.user.is_authenticated and request.user != ad.author:
        # TODO: Allow only one comment per user
        form = forms.NewComment(request.GET)
        if form.is_valid():
            models.Comment.objects.create(author=request.user,
                                          profile=ad.author,
                                          advertisement=ad,
                                          text=form.cleaned_data["comment"])
            context["comment_added"] = True

    # Processing deactivation
    if request.GET.get("deactivate") and ad.active and request.user == ad.author:
        ad.active = False
        ad.save()
        if request.GET.get("next") == "profile":
            return redirect("accounts:account")

    # Processing reactivation
    elif request.GET.get("activate") and not ad.active and request.user == ad.author:
        ad.active = True
        ad.save()
        if request.GET.get("next") == "profile":
            return redirect("accounts:account")

    # Processing delete
    elif request.GET.get("delete") and not ad.active and request.user == ad.author:
        ad.delete()
        return redirect("accounts:account")

    return render(request, "rentitapp/advertisement_detail.html", context=context)


# edit ad page
@login_required
def advertisement_edit(request, pk=None):
    ad = get_object_or_404(models.Advertisement, pk=pk)
    if ad.author != request.user:
        return HttpResponseRedirect("/")

    if request.method == 'POST':
        form = forms.EditAdvertisement(request.POST, request.FILES, instance=ad)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(f"/detail/{ad.id}?edited=1")
    else:
        form = forms.EditAdvertisement(instance=ad)
        return render(request, "rentitapp/advertisement_edit.html",
                      {'form': form, })


# create ad page
@login_required(login_url="/profile/login")
def advertisement_create(request):
    if request.method == 'POST':
        form = forms.EditAdvertisement(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author = request.user
            instance.save()

            return HttpResponseRedirect(f"detail/{instance.id}?success=1")
        else:
            print(form.errors)

    else:
        form = forms.EditAdvertisement()

    return render(request, "rentitapp/advertisement_edit.html", {'form': form, })
