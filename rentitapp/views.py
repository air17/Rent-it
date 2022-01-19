from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import ListView

from rentitapp import models, forms


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
        for ad in context["advertisement_list"]:
            if not ad.active:
                context["advertisement_list"].remove(ad)

        # removing new ads for non-premium
        if self.request.user.is_anonymous or not self.request.user.is_premium:
            for ad in context["advertisement_list"]:
                if ad.date_published > timezone.now() - timedelta(days=1):
                    context["advertisement_list"].remove(ad)

        # adding main photo
        for ad in context["advertisement_list"]:
            main_picture: list = models.AdvertisementImage.objects.filter(
                advertisement=ad, main=True)
            if main_picture:
                ad.main_photo = main_picture[0].image.url
            else:
                ad.main_photo = "/media/empty_photo.png"
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

    # Adding main picture
    main_picture = models.AdvertisementImage.objects.filter(
        advertisement=ad, main=True)
    if main_picture:
        context['main_picture'] = main_picture[0].image.url
    else:
        context['main_picture'] = "/media/empty_photo.png"

    # Adding additional pictures
    additional_pictures = []
    for adv_images in models.AdvertisementImage.objects.filter(
            advertisement=ad, main=False):
        additional_pictures.append(adv_images.image)
    context["additional_pictures"] = additional_pictures

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
            return redirect("rentitapp:account")

    # Processing reactivation
    elif request.GET.get("activate") and not ad.active and request.user == ad.author:
        ad.active = True
        ad.save()
        if request.GET.get("next") == "profile":
            return redirect("rentitapp:account")

    # Processing delete
    elif request.GET.get("delete") and not ad.active and request.user == ad.author:
        ad.delete()
        return redirect("rentitapp:account")

    return render(request, "rentitapp/advertisement_detail.html", context=context)


# edit ad page
@login_required
def advertisement_edit(request, pk=None):
    ad = get_object_or_404(models.Advertisement, pk=pk)
    if ad.author != request.user:
        return HttpResponseRedirect("/")

    old_pictures = models.AdvertisementImage.objects.filter(advertisement=ad, main=True)
    old_picture = old_pictures[0] if old_pictures else None

    if request.method == 'POST':
        form = forms.EditAdvertisement(request.POST, request.FILES, instance=ad)
        formset = forms.EditAdvertisementPictureFormset(request.POST, request.FILES,
                                                        instance=ad)
        img_form = forms.NewAdvertisementPicture(request.POST, request.FILES,
                                                 instance=old_picture, label_suffix=" main:")

        if form.is_valid() and formset.is_valid() and img_form.is_valid():
            form.save()

            formset.save()

            img_form = img_form.save(commit=False)
            img_form.advertisement = ad
            img_form.main = True
            img_form.save()

            return HttpResponseRedirect(f"/detail/{ad.id}?edited=1")
    else:
        form = forms.EditAdvertisement(instance=ad)
        formset = forms.EditAdvertisementPictureFormset(instance=ad,
                                                        queryset=models.AdvertisementImage.objects.filter(
                                                            advertisement=ad, main=False))
        img_form = forms.NewAdvertisementPicture(instance=old_picture, label_suffix=" main:")

    return render(request, "rentitapp/advertisement_edit.html",
                  {'form': form, "formset": formset, "main_pic_form": img_form})


# create ad page
@login_required(login_url="/profile/login")
def advertisement_create(request):
    if request.method == 'POST':
        form = forms.NewAdvertisement(request.POST, request.FILES)
        formset = forms.NewAdvertisementPictureFormset(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author = request.user
            instance.save()
            pic = request.FILES.getlist('main_picture')[0]
            image = models.AdvertisementImage.objects.create(advertisement=instance, image=pic, main=True)
            image.save()

            for f in formset:
                form = f.save(commit=False)
                form.advertisement = instance
                form.save()

            return HttpResponseRedirect(f"detail/{instance.id}?success=1")

    else:
        form = forms.NewAdvertisement()
        formset = forms.NewAdvertisementPictureFormset()

    return render(request, "rentitapp/advertisement_create.html", {'form': form, "formset": formset})
