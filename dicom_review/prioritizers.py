from django.db.models import Count
from django.conf import settings
from solo.models import SingletonModel
import loader

MAX_REVIEWERS = settings.MAX_REVIEWERS
# Simple algorithm that checks to see the number of years the studies span and
# returns one study per year
def one_per_year(candidate_studies, user, annotation_class = None):
    studies = []
    years = candidate_studies.dates('study_date', 'year')
    for period in years:
       this_year = candidate_studies.annotate(num_reviews=Count("radiologystudyreview"))\
           .filter(study_date__year=period.year, num_reviews__lt=MAX_REVIEWERS)\
           .exclude(radiologystudyreview__user_id=user.id).order_by("?")[:1]
       for study in this_year:
         studies.append(study)
    return studies

# Whether the list method is the global default or set on the user object explicitly does not matter. The workflow will be same
# Check to see if the user object has an associated list object if so use that one
# If not check to see if there is a global list object setup, if so use that one
# Otherwise just pull from the candidate_studies
def lists(candidate_studies, user, annotation_class = None):
    from models import Config

    study_list = (hasattr(user, 'study_list') and user.study_list) or Config.get_solo().default_study_list
    # if no lists are configured, just pass thru
    if not study_list:
        return candidate_studies

    studies = study_list.studies.exclude(radiologystudyreview__user_id = user.id)
    return studies

#TODO Cross Validate Algorithm that chooses studies and puts them on other users lists.

registry = loader.Registry(default=one_per_year, default_name = "one per year")
registry.register(lists, name = "lists")

loader.autodiscover()
