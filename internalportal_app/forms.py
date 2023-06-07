from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
#from django.contrib.auth.models import User

#This should only be pushed to the updates branch

from .models import Clients, statement_of_work, projects, avature_steps, project_metrics, Weblinks

class ClientCreationForm(UserCreationForm):
    name = forms.CharField(max_length=30)
    location = forms.CharField(max_length=30)

    class Meta:
        model = Clients
        fields = ['name', 'location']

class ClientChangeForm(UserChangeForm):

    class Meta:
        model = Clients
        fields = ['name', 'location']

class SOWCreationForm(UserCreationForm):
    name = forms.CharField(max_length=200)
    
    
    class Meta:
        model = statement_of_work
        fields = ['name', 'client', 'html', 'start_date']

class SOWChangeForm(UserChangeForm):
    
    class Meta:
        model = statement_of_work
        fields = ['name', 'client', 'html', 'start_date', 'end_date']

class ProjectCreationForm(UserCreationForm):
    name = forms.CharField(max_length=30)
    

    class Meta:
        model = projects
        fields = ['name', 'sow']

class ProjectChangeForm(UserChangeForm):
    
    class Meta:
        model = projects
        fields = ['name', 'sow']

class ClientSelectionForm(forms.ModelForm):
    client_name = forms.ModelChoiceField(queryset=Clients.objects.filter())

    class Meta:
        model = Clients
        fields =['client_name']

class SOWSelectionForm(forms.ModelForm):
    sow = forms.ModelChoiceField(queryset=statement_of_work.objects.filter())

    class Meta:
        model = statement_of_work
        fields = ['sow']

class AvatureSteps(forms.ModelForm):
    name = forms.CharField(max_length=200)
    
    class Meta:
        model = avature_steps
        fields = ['name']
        
class AvatureStepsChange(forms.ModelForm):
        
    class Meta:
        model = avature_steps
        fields = ['name']
        
class AddProjectMetrics(forms.ModelForm):
    
    class Meta:
        model = project_metrics
        fields = ['external_step','sow', 'step', 'metric_value', 'start_date']
        
class ChangeProjectMetrics(forms.ModelForm):
    
    class Meta:
        model = project_metrics
        fields = ['external_step','sow', 'step', 'metric_value', 'start_date']    

class WeblinksForm(forms.ModelForm):
    
    class Meta:
        model = Weblinks
        fields = ("title", "site_url", "logo_url", "description")
    