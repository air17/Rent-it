from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import formset_factory, inlineformset_factory

from rentitapp.models import Advertisement, AdvertisementImages, User


class EditAdvertisement(forms.ModelForm):
    class Meta:
        model = Advertisement
        fields = ("name", "category", "description", "price", "address")


class NewAdvertisement(EditAdvertisement):
    main_picture = forms.ImageField(label="Основное фото")


class NewAdvertisementPicture(forms.ModelForm):
    class Meta:
        model = AdvertisementImages
        fields = ("image", )


NewAdvertisementPictureFormset = formset_factory(form=NewAdvertisementPicture,
                                                 extra=5, max_num=15, absolute_max=15)

EditAdvertisementPictureFormset = inlineformset_factory(parent_model=Advertisement,
                                                        model=AdvertisementImages,
                                                        form=NewAdvertisementPicture,
                                                        extra=1, max_num=15, absolute_max=15)


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "phone", "picture")


class NewComment(forms.Form):
    comment = forms.CharField(required=True, widget=forms.Textarea())
