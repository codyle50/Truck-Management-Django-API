from django.db import models
from user_account_app.models import User, Driver

# Create your models here.




#===========================================================================
#   TRUCK MODEL
#===========================================================================
class Truck(models.Model):
    plate = models.CharField(max_length=256)
    nickname = models.CharField(max_length=256)
    owner = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, default=None)
    current_driver = models.ForeignKey(Driver, null=True, on_delete=models.SET_NULL, default=None)

    def __str__(self):
        return self.plate + " - " + self.nickname



#===========================================================================
#   QUARTER MODEL
#===========================================================================
class Quarter(models.Model):
    number = models.IntegerField(default=0)
    year = models.IntegerField(default=0)

    total_toll_miles = models.FloatField(default=0.0)
    total_non_toll_miles = models.FloatField(default=0.0)
    total_gallons = models.FloatField(default=0.0)
    total_taxes = models.FloatField(default=0.0)
    total_mpg = models.FloatField(default=0.0)

    truck = models.ForeignKey(Truck, null=True, on_delete=models.SET_NULL, default=None)

    def __str__(self):
        return "Quarter " + str(self.number) + " - " + str(self.year)


#===========================================================================
#   New Entry
#===========================================================================
class NewEntry(models.Model):
    day = models.IntegerField(default=0)
    month = models.IntegerField(default=0)
    year = models.IntegerField(default=0)

    total_toll_miles = models.FloatField(default=0.0)
    total_non_toll_miles = models.FloatField(default=0.0)
    total_gallons = models.FloatField(default=0.0)
    price = models.FloatField(default=0.0)
    usa_state = models.CharField(max_length=256, default="-1")
    current_quarter = models.IntegerField(default=1)
    truck = models.ForeignKey(Truck, null=True, on_delete=models.SET_NULL, default=None)
    driver = models.ForeignKey(Driver, null=True, on_delete=models.SET_NULL, default=None)

    def __str__(self):
        return "New Entry " + str(self.month) + "/" + str(self.day) + "/" + str(self.year)



#===========================================================================
#   STATE REPORT MODEL
#===========================================================================
class StateReport(models.Model):
    name = models.CharField(max_length=256)
    initials = models.CharField(max_length=256)

    total_toll_miles = models.FloatField(default=0.0)
    total_non_toll_miles = models.FloatField(default=0.0)
    total_gallons = models.FloatField(default=0.0)
    total_taxes = models.FloatField(default=0.0)
    total_mpg = models.FloatField(default=0.0)

    quarter = models.ForeignKey(Quarter, null=True, on_delete=models.SET_NULL, default=None)

    def __str__(self):
        return self.name + " (" + self.initials + ")"



#===========================================================================
#   STATE TAXES MODEL
#===========================================================================
class StateTaxes(models.Model):
    name = models.CharField(max_length=256)
    initials = models.CharField(max_length=256)
    # number equals the quarter's number
    number = models.IntegerField(default=0)
    year = models.IntegerField(default=0)
    tax = models.FloatField(default=0.0)
    fuel = models.CharField(max_length=256, default='Biodiesel')

    class Meta:
        verbose_name_plural='state taxes'

    def __str__(self):
        return self.name + " (" + self.initials + ") - Quarter " + self.number + " - " + self.year
