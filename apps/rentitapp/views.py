from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from . import models, forms
from .constants import days_till_free
from .services import process_comment


def advertisement_list(request):
    ads_list = models.Advertisement.objects.all()

    context = {}

    # sorting
    sort_by = request.GET.get("sort")
    if sort_by in ("name", "date_published", "price"):
        ads_list = ads_list.order_by(sort_by)
        context["sort"] = sort_by
        if request.GET.get("desc"):
            ads_list = ads_list.reverse()
            context["sort"] += "_d"

    # adding available accommodation categories to context
    context["categories"] = [*models.Advertisement.FlatCategory]

    # filtering categories
    category_selected: str = request.GET.get("category")
    if category_selected in models.Advertisement.FlatCategory.values[1:]:
        context["category_selected"] = category_selected
        ads_list = ads_list.filter(category=category_selected)

    # removing deactivated ads
    ads_list = ads_list.filter(active=True)

    # removing new ads for non-premium
    if request.user.is_anonymous or not request.user.is_premium:
        ads_list = ads_list.filter(date_published__lte=timezone.now() - timedelta(days=days_till_free))

    paginator = Paginator(ads_list, 9)  # Show 9 ads per page.
    page_number = request.GET.get("page")

    # adding paginated ads to context
    context["advertisement_list"] = paginator.get_page(page_number)

    return render(request, "rentitapp/advertisement_list.html", context)


# advertisement details page
def advertisement_detail(request, pk=None):
    ad = get_object_or_404(models.Advertisement, pk=pk)

    # Redirect if ad is new and user is not premium
    if (
        request.user != ad.author
        and (request.user.is_anonymous or not request.user.is_premium)
        and ad.date_published > timezone.now() - timedelta(days=days_till_free)
    ):
        return HttpResponseRedirect("/")

    # Setting up context, adding category label, default variables, comment form
    context = {
        "advertisement": ad,
        "category": ad.FlatCategory(ad.category).label,
        "just_added": False,
        "comment_added": False,
        "new_comment": forms.NewComment(),
    }

    # Showing notification when added or edited
    if request.GET.get("success") or request.GET.get("edited"):
        context["just_added"] = True
        context["status_text"] = "Объявление успешно размещено!"
        if request.GET.get("edited"):
            context["status_text"] = "Объявление отредактировано"

    # Processing adding comment
    elif request.GET.get("comment") and request.user.is_authenticated and request.user != ad.author:
        form = forms.NewComment(request.GET)
        context["comment_added"] = process_comment(form, request.user, ad)

    # Processing deactivation
    elif request.GET.get("deactivate") and ad.active and request.user == ad.author:
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

    # Processing deletion
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

    if request.method == "POST":
        form = forms.EditAdvertisement(request.POST, request.FILES, instance=ad)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(f"/detail/{ad.id}?edited=1")
    else:
        form = forms.EditAdvertisement(instance=ad)

    context = {"form": form}
    return render(request, "rentitapp/advertisement_edit.html", context)


# create ad page
@login_required(login_url="/profile/login")
def advertisement_create(request):
    if request.method == "POST":
        form = forms.EditAdvertisement(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author = request.user
            instance.save()

            return HttpResponseRedirect(f"detail/{instance.id}?success=1")
    else:
        form = forms.EditAdvertisement()

    context = {"form": form}
    return render(request, "rentitapp/advertisement_edit.html", context)
