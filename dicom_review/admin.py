from django.contrib import admin
from dicom_models.staging.models import RadiologyStudy, RadiologyStudyReview
from models import StudyList, Reviewer, Config
from solo.admin import SingletonModelAdmin

class StudyInline(admin.StackedInline):
    model = StudyList.studies.through

class ListAdmin(admin.ModelAdmin):
    inlines = [StudyInline]
    exclude = ('studies',);

admin.site.register(StudyList, ListAdmin)
admin.site.register(Reviewer)
admin.site.register(Config, SingletonModelAdmin)
admin.site.register(RadiologyStudy)
admin.site.register(RadiologyStudyReview)
