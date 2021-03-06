from django.contrib import admin

from .models import Advertisement, Comment


class AdAdmin(admin.ModelAdmin):
    """Customizes list view and adds search and filters for advertisements"""

    list_display = (
        "name",
        "category",
        "price",
        "author",
        "date_published",
    )
    list_filter = ("date_published",)
    search_fields = ("name", "description")


admin.site.register(Advertisement, AdAdmin)
admin.site.register(Comment)
