from django.contrib import admin
from django.contrib.admin import ModelAdmin
from .models import YookassaPayment


class CustomModel(ModelAdmin):
    list_display = (
        "id",
        "user",
        "amount",
        "status",
        "created_at",
        "processed",
    )


admin.site.register(YookassaPayment, CustomModel)
