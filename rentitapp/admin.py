from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from rentitapp.models import User, Advertisement, AdvertisementImages, Comment


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('picture', 'first_name', 'last_name', 'phone')}),
        (_('Permissions'), {'fields': ('is_premium', 'is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_premium')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)


class AdAdmin(admin.ModelAdmin):
    class ImagesInline(admin.TabularInline):
        model = AdvertisementImages
        extra = 1
    inlines = [ImagesInline]
    list_display = ('name', 'category', 'price', 'author', 'date_published')
    list_filter = ['date_published']
    search_fields = ['name', 'description']


admin.site.register(User, CustomUserAdmin)
admin.site.register(Advertisement, AdAdmin)
admin.site.register(Comment)
