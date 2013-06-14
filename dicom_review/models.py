from django.contrib.auth.models import AbstractUser
from django.db import models
from dicom_models.staging.models import RadiologyStudy
from prioritizers import registry as prioritizers
from solo.models import SingletonModel

class Prioritizer(models.Model):
    pass

class StudyList(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    studies = models.ManyToManyField(RadiologyStudy)

    def __unicode__(self):
        if self.name:
            return u'%s' % self.name
        return u'Study List Object'

class Reviewer(AbstractUser):
    prioritizer = models.CharField(max_length=100, blank=True, null=True,
        choices=prioritizers.choices)
    study_list = models.ForeignKey(StudyList, null=True, blank=True)

class Config(SingletonModel):
    default_prioritizer = models.CharField(max_length=100, blank=True, null=True,
        choices=prioritizers.choices)
    default_study_list = models.ForeignKey(StudyList, null=True, blank=True)


    def __unicode__(self):
        return u'App configuration'

    class Meta:
            verbose_name = "App Configuration"
            verbose_name_plural = "App Configuration"
