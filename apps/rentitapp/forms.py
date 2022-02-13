from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Advertisement


class EditAdvertisement(forms.ModelForm):
    """Advertisement creation and editing form"""

    class Meta:
        model = Advertisement
        fields = (
            "name",
            "category",
            "description",
            "price",
            "address",
            "picture",
        )


class RegistrationForm(UserCreationForm):
    """Custom User registration form"""

    class Meta:
        model = get_user_model()
        fields = (
            "email",
            "first_name",
            "last_name",
            "phone",
            "picture",
        )


class NewComment(forms.Form):
    """Comment creation form"""

    comment = forms.CharField(required=True, widget=forms.Textarea())
