import json
from dicom_models.staging.models import RadiologyStudy
from dicom_models.staging.models import RadiologyStudyReview as StudyReview
from django.db import models
from django.db.models import Count
from django.db.models import Q
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.conf import settings
from django.template import RequestContext
from django.forms import ModelForm
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required

MAX_REVIEWERS = settings.MAX_REVIEWERS

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
    studies = []
    candidate_studies = RadiologyStudy.objects.filter(exclude=False, image_published=False, original_study_uid__isnull=False)
    years = candidate_studies.dates('study_date', 'year')
    for period in years:
       this_year = candidate_studies.values('id').annotate(num_reviews=Count("radiologystudyreview"))\
           .filter(study_date__year=period.year, num_reviews__lt=MAX_REVIEWERS)\
           .exclude(radiologystudyreview__user_id=request.user.id).order_by("?")[:1]
       for study in this_year:
         studies.append(study['id'])
    studies = RadiologyStudy.objects.filter(id__in=studies)[:settings.MAX_STUDIES_PER_PAGE]

    high_risk = False
    for study in studies:
        if study.high_risk_flag:
            high_risk = True
            break

    return render_to_response("index.html", {
        'high_risk': high_risk,
        'always_show_high_risk': settings.ALWAYS_SHOW_HIGH_RISK,
        'studies':studies,
        'saved':prev_saved,
        'project_name': settings.DICOM_PROJECT_NAME,
        'studycentric_link': settings.STUDYCENTRIC_LINK
    }, RequestContext(request))

