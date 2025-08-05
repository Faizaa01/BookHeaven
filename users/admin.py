from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username','email', 'first_name', 'last_name', 'is_active')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'groups')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'address')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone_number', 'password1', 'password2', 'is_staff', 'is_active')
        }),
    )
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('username',)


admin.site.register(User, CustomUserAdmin)
