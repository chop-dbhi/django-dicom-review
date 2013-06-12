from django.contrib import admin
from dicom_models.staging.models import RadiologyStudy, RadiologyStudyReview

admin.site.register(RadiologyStudy)
admin.site.register(RadiologyStudyReview)
