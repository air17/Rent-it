from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms import formset_factory, inlineformset_factory

from rentitapp.models import Advertisement, AdvertisementImage


class EditAdvertisement(forms.ModelForm):
    class Meta:
        model = Advertisement
        fields = ("name", "category", "description", "price", "address")


class NewAdvertisement(EditAdvertisement):
    main_picture = forms.ImageField(label="Основное фото")


class NewAdvertisementPicture(forms.ModelForm):
    class Meta:
        model = AdvertisementImage
        fields = ("image", )


NewAdvertisementPictureFormset = formset_factory(form=NewAdvertisementPicture,
                                                 extra=3, max_num=15, absolute_max=15)

EditAdvertisementPictureFormset = inlineformset_factory(parent_model=Advertisement,
                                                        model=AdvertisementImage,
                                                        form=NewAdvertisementPicture,
                                                        extra=1, max_num=15, absolute_max=15)


class RegistrationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ("email", "first_name", "last_name", "phone", "picture")


class NewComment(forms.Form):
    comment = forms.CharField(required=True, widget=forms.Textarea())
