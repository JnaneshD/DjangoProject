from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
# Create your models here.
class UserIncome(models.Model):
    amount = models.FloatField()#Decimal value
    date = models.DateField(default=now)
    description = models.TextField()
    owner = models.ForeignKey(to=User,on_delete=models.CASCADE)
    source = models.CharField(max_length=266)
    class Meta:
        ordering: ['-date']
    def __str__(self):
        return self.source

class Source(models.Model):
    name = models.CharField(max_length=266)
    def __str__(self):
        return self.name
    