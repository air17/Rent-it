from django import forms

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


class NewComment(forms.Form):
    """Comment creation form"""

    comment = forms.CharField(required=True, widget=forms.Textarea())
