from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from . import forms, models
from .constants import days_till_free
from .services import process_comment


def advertisement_list(request):
    """Displays paginated list of public advertisements."""

    ads_list = models.Advertisement.objects.all()

    context = {}

    # Sorting ads
    sort_by = request.GET.get("sort")
    if sort_by in ("name", "date_published", "price"):
        ads_list = ads_list.order_by(sort_by)
        context["sort"] = sort_by
        if request.GET.get("desc"):
            ads_list = ads_list.reverse()
            context["sort"] += "_d"

    # Adding available accommodation categories to context
    context["categories"] = [*models.Advertisement.FlatCategory]

    # Filtering categories
    category_selected: str = request.GET.get("category")
    if category_selected in models.Advertisement.FlatCategory.values[1:]:
        context["category_selected"] = category_selected
        ads_list = ads_list.filter(category=category_selected)

    # Removing deactivated ads
    ads_list = ads_list.filter(active=True)

    # Removing new ads for non-premium
    if request.user.is_anonymous or not request.user.is_premium:
        ads_list = ads_list.filter(date_published__lte=timezone.now() - timedelta(days=days_till_free))

    paginator = Paginator(ads_list, 9)  # Show 9 ads per page.
    page_number = request.GET.get("page")

    # Adding paginated ads to the context
    context["advertisement_list"] = paginator.get_page(page_number)

    return render(request, "rentitapp/advertisement_list.html", context)


def advertisement_detail(request, pk):
    """Displays an advertisement and comment form."""

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
        "new_comment": forms.NewComment(),
    }

    # Showing notification when added or edited
    if request.GET.get("success") or request.GET.get("edited"):
        context["just_added"] = True
        context["status_text"] = "Объявление успешно размещено!"
        if request.GET.get("edited"):
            context["status_text"] = "Объявление отредактировано"
    context["comment_added"] = request.GET.get("comment_added")

    return render(request, "rentitapp/advertisement_detail.html", context=context)


@login_required
def advertisement_edit(request, pk=None):
    """Displays advertisement editing form and processes it."""

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


@login_required
def advertisement_create(request):
    """Displays advertisement creation form and processes it."""

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


@login_required
def advertisement_process(request, pk):
    """Processes advertisement deactivation, reactivation and deletion."""

    ad = get_object_or_404(models.Advertisement, pk=pk)

    if request.user != ad.author:
        return redirect("/")

    # Processing deactivation
    if request.GET.get("deactivate") and ad.active:
        ad.active = False
        ad.save()
        if request.GET.get("next") == "profile":
            return redirect("accounts:account")

    # Processing reactivation
    elif request.GET.get("activate") and not ad.active:
        ad.active = True
        ad.save()
        if request.GET.get("next") == "profile":
            return redirect("accounts:account")

    # Processing deletion
    elif request.GET.get("delete") and not ad.active:
        ad.delete()
        return redirect("accounts:account")

    return redirect("rentitapp:advertisement", pk=pk)


@login_required
def comment_processing(request, pk):
    """Processing adding comment"""

    ad = get_object_or_404(models.Advertisement, pk=pk)

    if request.user != ad.author:
        form = forms.NewComment(request.GET)
        if process_comment(form, request.user, ad):
            return redirect(reverse("rentitapp:advertisement", args=(pk,)) + "?comment_added=1")

    return redirect(reverse("rentitapp:advertisement", args=(pk,)) + "?comment_added=error")
