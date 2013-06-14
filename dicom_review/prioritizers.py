from django.db.models import Count
from django.conf import settings
import loader

MAX_REVIEWERS = settings.MAX_REVIEWERS

def one_per_year(candidate_studies, user):
    studies = []
    years = candidate_studies.dates('study_date', 'year')
    for period in years:
       this_year = candidate_studies.values('id').annotate(num_reviews=Count("radiologystudyreview"))\
           .filter(study_date__year=period.year, num_reviews__lt=MAX_REVIEWERS)\
           .exclude(radiologystudyreview__user_id=user.id).order_by("?")[:1]
       for study in this_year:
         studies.append(study['id'])
    return studies

registry = loader.Registry(default=one_per_year, default_name = "one per year")
loader.autodiscover('prioritizer')
