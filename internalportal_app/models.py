from django.db import models
from users_app import models as uamodels


# Create your models here.
class Clients(models.Model):
    name = models.CharField(max_length=30)
    location = models.CharField(max_length=30)

    def __str__(self):
        return self.name
       
    class Meta:
        
        managed = True
        verbose_name =  "Clients"
        verbose_name_plural =  "Clients"

class statement_of_work(models.Model):
    client = models.ForeignKey(Clients, on_delete=models.CASCADE)
    name = models.CharField(max_length = 200)
    html = models.CharField(null=True, max_length =200)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name
    
    class Meta:
        pass

class projects(models.Model):
    sow = models.ForeignKey(statement_of_work, on_delete=models.CASCADE)
    name = models.CharField(max_length = 200)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name
  
    class Meta:
        pass
    
class avature_steps(models.Model):
    name = models.CharField(max_length = 200)
    
    def __str__(self):
        return self.name
    
class project_metrics(models.Model):
    sow = models.ForeignKey(statement_of_work, on_delete=models.CASCADE)
    step = models.ForeignKey(avature_steps, on_delete=models.CASCADE)
    external_step = models.CharField(max_length = 200)
    metric_value = models.FloatField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
        
    def __str__(self):
        return self.external_step 

class Weblinks(models.Model):
    title = models.CharField(max_length=50)
    site_url = models.CharField(max_length=200)
    logo_url = models.CharField(max_length=200)
    description = models.CharField(max_length=30)

    def __str__(self):
        return self.title
    
class CandidateNote(models.Model):
    candidate_id = models.CharField(max_length=7)
    candidate_note = models.TextField()
    written_by = models.ForeignKey(uamodels.CustomUser, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.candidate_note



    