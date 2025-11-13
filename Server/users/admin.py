from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_user', 'is_staff')
    list_filter = ('is_user', 'is_staff', 'is_superuser', 'is_active')
    
    fieldsets = (
        (None, {'fields': ('username', 'phone','password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'country_code', 'phone_number')}),
        (_('Permissions'), {'fields': ('is_active', 'is_user', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined', 'last_logout')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'username','phone_number','first_name', 'last_name')
    ordering = ('-id',)

admin.site.register(User, UserAdmin)