from django.db import models


# Create your models here.
class Duck(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=200)

    def __str__(self):
        return "(" + str(self.id) + ") - " + self.name + " - " + self.description


class DuckFact(models.Model):
    duck = models.ForeignKey(Duck, on_delete=models.CASCADE)
    fact = models.CharField(max_length=200)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return "(" + str(self.rating) + ") : " + self.fact
