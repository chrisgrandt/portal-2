from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomCreationForm,CustomChangeForm
from .models import CustomUser, Dashboards, DashboardAccess

def make_employee(modeladmin, request, queryset):
    queryset.update(is_employee = True)
make_employee.short_description = "Mark Selected as Employee"

def make_admin(modeladmin, request, queryset):
    queryset.update(is_adminUser = True)
make_admin.short_description = "Mark Selected as Administrator"

class CustomUserAdmin(UserAdmin):
    add_form = CustomCreationForm
    form = CustomChangeForm
    model = CustomUser
    list_display = ['first_name','last_name','email','username','is_employee', 'is_adminUser']
    actions = [make_employee, make_admin]

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Dashboards)
admin.site.register(DashboardAccess)
