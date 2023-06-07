from urllib import request
from django import template
from users_app import models

register = template.Library()

@register.filter(name='zip')
def zip_lists(a,b,c):
    return zip(a,b,c)

@register.simple_tag
def setvar(val=None):
    return val

@register.filter(name='company_is')
def company_is(user, company):
    company = models.ClientCompanies.objects.get(company_name=company)
    return True if company in user.company.all() else False

