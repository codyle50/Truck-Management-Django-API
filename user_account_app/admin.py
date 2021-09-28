from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _
from .models import *

# Register your models here.


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Extra Info'), {'fields' : ('company_name','one_click_purchasing', 'stripe_customer_id')}),
        (_('Account Finance Info'), {'fields' : ('account_category','paid_untill')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
)

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'phone'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'id', 'is_staff','is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    # list_filter = ['staff','admin']

admin.site.register(AccountCategory)
admin.site.register(DriverProfile)
admin.site.register(Payment)
