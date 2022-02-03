from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None,
         {'fields': (
             'email',
             'password',
         )}),

        ('Personal info',
         {'fields': (
             'picture',
             'first_name',
             'last_name',
             'phone',
         )}),

        ('Permissions',
         {'fields': (
             'is_premium',
             'is_active',
             'is_staff',
             'is_superuser',
             'groups',
             'user_permissions',
         )}),

        ('Important dates',
         {'fields': (
             'last_login',
             'date_joined',
         )}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    list_display = ('email',
                    'first_name',
                    'last_name',
                    'is_staff',
                    'is_premium',
                    )
    search_fields = ('email',
                     'first_name',
                     'last_name',
                     )
    ordering = ('email',)


admin.site.register(User, CustomUserAdmin)
