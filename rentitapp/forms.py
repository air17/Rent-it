from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from rentitapp.models import Advertisement


class EditAdvertisement(forms.ModelForm):
    class Meta:
        model = Advertisement
        fields = ("name", "category", "description", "price", "address", "images")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["images"].required = True
        self.fields["images"].max_number_of_images = 3

        self.helper = FormHelper(self)
        self.helper.layout.append(
            Submit("Submit", "Сохранить",
                   css_class="gallery-widget-submit-button"))


class RegistrationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ("email", "first_name", "last_name", "phone", "picture")


class NewComment(forms.Form):
    comment = forms.CharField(required=True, widget=forms.Textarea())
