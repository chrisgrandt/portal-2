from cProfile import label
from calendar import c
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
#from django.contrib.auth.models import User

from .models import CustomUser, DashboardAccess, Dashboards, CandidatePresentation, ClientCompanies, PresentationAccess

class CustomCreationForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))
    last_name = forms.CharField(max_length=30)

    class Meta:
        model = CustomUser
        fields = ['first_name','last_name', 'username','email', 'password1', 'password2', 'is_employee', 'is_manager', 'company']

class CustomChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ['first_name','last_name', 'username','email', 'is_employee', 'is_adminUser', 'is_manager', 'company']

class DashboardAdditionForm(forms.ModelForm):

    class Meta:
        model = Dashboards
        fields = ['dashboard_name', 'dashboard_reference', 'related_company']
        labels = {'dashboard_reference' : 'Iframe Code'}

class DashboardAccessForm(forms.ModelForm):
       
    class Meta:
        model = DashboardAccess
        fields = ['user_reference', 'related_dashboard']
        labels = {'user_reference':'User'}

class CompanyAdditionForm(forms.ModelForm):

    class Meta:
        model = ClientCompanies
        fields = ['company_name', 'logo_url']
        labels = {'company_name':'Company Name', 'logo_url': 'Logo URL'}

class CandidatePresentationAdditionForm(forms.ModelForm):
    
    class Meta:
        model = CandidatePresentation
        fields = ['file_name', 'display_name', 'company_name', 'extension_value']
        label = {'file_name':'Name of CSV File', 'display_name': 'Name to Display', 'company_name': 'Company'}

class PresentationAccessForm(forms.ModelForm):

    class Meta:
        model = PresentationAccess
        fields = ['user_reference', 'related_presentation']
        labels = {'user_reference': 'User', 'related_presentation': 'Presentation'}
        





