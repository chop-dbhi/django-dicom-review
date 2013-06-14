import json
from dicom_models.staging.models import RadiologyStudy
from dicom_models.staging.models import RadiologyStudyReview as StudyReview
from models import Config
from django.db import models
from django.db.models import Q
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.conf import settings
from django.template import RequestContext
from django.forms import ModelForm
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from prioritizers import registry as prioritizers

MAX_REVIEWERS = settings.MAX_REVIEWERS
config = Config.get_solo()

# Default priority function
# Takes allows 1 study per year in the range of years across all
# studies in the database

# Create the form class
class ReviewForm(ModelForm):
    class Meta:
        model = StudyReview

@login_required
@never_cache
def review(request):
    saved = 0 
    if request.method == 'POST':
        reviews = json.loads(request.raw_post_data)
        for review in reviews:
            review["user_id"] = request.user.id
            form = ReviewForm(review)
            if form.is_valid():
                form.save()
                saved+=1
        return HttpResponse('{"saved":%d}' % saved, content_type = "application/json")
    else:
        return studies_page(request, saved)

@login_required
def studies_page(request, prev_saved):
    reviewer = request.user
    # Here we determine studies that are eligible for review
    candidate_studies = RadiologyStudy.objects.filter(exclude=False, image_published=False, original_study_uid__isnull=False)
    # We must decide what method to use for choosing the reviews displayed to the user
    # First we check to see if the user object has a priority method defined
    # If it does we use that one.
    # Otherwise, there will be a site wide default algorithm, and by default this will be set to one_per_year

    if reviewer.prioritizer:
        prioritizer_name = reviewer.prioritizer
    elif config.default_prioritizer:
        prioritizer_name = config.default_prioritizer
    else:
        prioritizer_name = 'default'

    prioritizer = prioritizers.get(prioritizer_name)

    studies = prioritizer(candidate_studies, request.user, annotation_class=StudyReview)
    studies = studies[:settings.MAX_STUDIES_PER_PAGE]

    high_risk = False
    for study in studies:
        if study.high_risk_flag:
            high_risk = True
            break

    return render_to_response("index.html", {
        'high_risk': high_risk,
        'always_show_high_risk': settings.ALWAYS_SHOW_HIGH_RISK,
        'warn_unviewed': settings.WARN_UNVIEWED,
        'studies':studies,
        'saved':prev_saved,
        'project_name': settings.DICOM_PROJECT_NAME,
        'studycentric_link': settings.STUDYCENTRIC_LINK
    }, RequestContext(request))

