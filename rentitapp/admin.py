from django.contrib import admin

from rentitapp.models import Advertisement, AdvertisementImages, Comment


class AdAdmin(admin.ModelAdmin):
    class ImagesInline(admin.TabularInline):
        model = AdvertisementImages
        extra = 1
    inlines = [ImagesInline]
    list_display = ('name', 'category', 'price', 'author', 'date_published')
    list_filter = ['date_published']
    search_fields = ['name', 'description']


admin.site.register(Advertisement, AdAdmin)
admin.site.register(Comment)
