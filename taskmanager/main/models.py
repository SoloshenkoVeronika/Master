from django.db import models

# Create your models here.

class Installation (models.Model):
    title = models.CharField('Name', max_length=50)
    #installation latitude in degrees
    latitude = models.FloatField('Latitude')
    #installation longitude in degrees
    longitude = models.FloatField('Latitude')
    #require time
    r_time = models.FloatField('Require_Time')
    #flag
    c_flaf = models.FloatField('Flag c', default='101')
    #flag
    number_of_people = models.IntegerField('People')
    #flag
    prob_accident = models.FloatField('Probability_ac')
    # methods
    def get_id(self):
        return self.id

    def get_title(self):
        return self.title

    def get_r_time(self):
        return self.r_time

    def get_lat(self):
        return self.latitude

    def get_lon(self):
        return self.longitude

    def get_c_flaf(self):
        return self.c_flaf

    def get_people(self):
            return self.number_of_people

    def get_c_accident(self):
        return self.prob_accident

    def __str__(self):
        return self.title


class ERRV (models.Model):
    title = models.CharField('Name', max_length=50)
    # ERRV latitude in degrees
    latitude = models.FloatField('Latitude')
    # ERRV longitude in degrees
    longitude = models.FloatField('Latitude')
    # ERRV probability
    prob = models.FloatField('Probability')
    # ERRV type of solution
    type_solution = models.FloatField('Solution', default='201')

    # methods
    def get_id(self):
        return self.id

    def get_title(self):
        return self.title

    def get_lat(self):
        return self.latitude

    def get_lon(self):
        return self.longitude

    def get_type_solution(self):
        return self.type_solution

    def get_prob(self):
        return self.prob

    def __str__(self):
        return self.title


