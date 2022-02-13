from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import PremiumSubscription


class CustomModel(ModelAdmin):
    """Customizes list view for PremiumSubscription model"""

    list_display = (
        "__str__",
        "start_date",
        "expiration_date",
    )


admin.site.register(PremiumSubscription, CustomModel)
