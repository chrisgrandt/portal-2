from unittest.util import _MAX_LENGTH
from django.contrib.auth.models import AbstractUser
from django.db import models

class ClientCompanies(models.Model):
    company_name = models.TextField()
    logo_url = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.company_name

class CustomUser(AbstractUser):
    is_employee = models.BooleanField(default=False)
    is_client = models.BooleanField(default=False)
    is_adminUser = models.BooleanField(default=False)
    is_real = models.BooleanField(default=False)
    is_manager = models.BooleanField(default= False)
    avature_id = models.PositiveIntegerField(null=True, blank=True)
    company = models.ForeignKey(ClientCompanies, on_delete=models.CASCADE, null=True, blank=True)
       
    def __str__(self):
        return self.username

class Dashboards(models.Model):
    dashboard_name = models.TextField()
    dashboard_reference = models.TextField()
    related_company = models.ForeignKey(ClientCompanies, on_delete=models.CASCADE, null=True, blank=True)
        
    def __str__(self):
        return self.dashboard_name
    
class DashboardAccess(models.Model):
    user_reference = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    related_dashboard = models.ForeignKey(Dashboards, on_delete=models.CASCADE)

class CandidatePresentation(models.Model):
    file_name = models.TextField()
    extension_value = models.TextField(null=True)
    display_name = models.TextField()
    company_name = models.ForeignKey(ClientCompanies, blank=True ,on_delete=models.CASCADE)

    def __str__(self):
        return self.display_name

class PresentationAccess(models.Model):
    user_reference = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    related_presentation = models.ForeignKey(CandidatePresentation, on_delete=models.CASCADE)










