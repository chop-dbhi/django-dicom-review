# Django DICOM Study Review App

# What is the Django DICOM Study Review App?
This is a simple Django application to serve up DICOM studies for manual review before use within a research project. It should be used in conjunction with [StudyCentric](https://github.com/cbmi/studycentric) which will display the studies.

# Screenshot
<center>
<img src="https://raw.github.com/cbmi/django-dicom-review/master/dicom_review.png"/>
</center>

# Features
1. High Risk Flag - Studies can be flagged as high risk. The reviewer will be notified in the app.
1. Customize studies to be reviewed - Control how the system selects the studies to be reviewed. For example, you might want to show all MR studies before CT. This can be customized globally or on a per user basis
1. Lists - Assign each user a list of a studies to review.

# Installation
To install, clone the repository and run 


```pip install -U -r requirements.txt```

This will install all dependencies.

# Setup

Once the requirements are all installed, you should just be able to run

`python manage.py syncdb`

and be up and running.

Once installed you will have to add studies to the system. This can be done manually using the admin interface, but for convenience there is a [DataExpress](http://dataexpress.research.chop.edu/) ETL script that will pull all the studies out of a [dcm4chee](http://www.dcm4che.org/confluence/display/ee2/Home) database [schema](http://www.dcm4che.org/confluence/download/attachments/496/pacstables_dcm4chee_216.jpg) and import them into the schema required by this application. See the section below for more details on the ETL script if you would like to use it.

## ETL script

The ETL script can be found in etl/import_studies.scala. The script is written using the [DataExpress](http://dataexpress.research.chop.edu/) framework. It reads the two property files (samples can be found in the conf directory), for a source and destination database. It will grab all of the studies from the `study` table in the source database and create a row for each study in the dicom_review database with sensible defaults. To run the script, follow these steps:


1. Install Scala on your system
2. Download the [DataExpress jar](https://github.com/downloads/cbmi/dataexpress/DataExpress-0.9.0-jar-with-dependencies.jar)
3. Edit the conf/pacsdb.properties file so that points to your dcmchee database.
4. Edit the conf/djangodb.properties file so that is points to the database this review application is running in.
5. Run the following commands

```
scala -cp "/path/to/DataeDpress.jar" etl/import_studies.scala
```

# Settings
There are a couple of settings defined in global_settings.py that can be overridden

1. DICOM\_PROJECT_NAME - This is the name of the project you are anonymizing images for. It is just used within the template and is not important. Defaults to "project"
2. STUDYCENTRIC_LINK - To allow users to view the studies, this application links off to a [StudyCentric](https://github.com/cbmi/studycentric) instance. Place the url to your [StudyCentric](https://github.com/cbmi/studycentric) instance here.
3. MAX_REVIEWERS - Defines the maximum number of users that can review a single study before it is not shown to anyone anymore. See the Customization section below for details.
4. MAX\_STUDIES\_PER__PAGE - The maximum number of studies to show a reviewer on a single page. Defaults to 10.
5. WARN_UNVIEWED - Whether or not to warn the reviewer if the app detects they are reviewing a study that they have not yet viewed. Defaults to True.
6. ALWAYS\_SHOW\_HIGH_RISK - For studies marked as High Risk, the app will display a column with a warning to the user. By default, if no studies on the page are high risk, the column will be omitted. Set this to True to override.


# Customization

The main customization point in this app is setting which studies the system will select to review first. This is determined by the default_prioritizer setting on the `App Configuration` (view and change in the Admin interface). This can be overridden on a per_user level by setting the prioritizer setting on the user's object (in the Admin interface). By default, the system uses a prioritizer called `one per year` that looks at all the studies in the system and returns one study from each year. There is another built-in prioritizer called `lists` that can be used to assign preset lists of studies to each user (or set a global list to be used for all users).

## Setting lists of studies to be reviewed

First create a list of studies. This can be done in the Admin interface under `Study Lists`. Once a study list has been created you can set it as the default_study_list on the `App Configuration` object in the Admin or as the study_list on individual users in the system. You can create different study lists and set them on different users to divide up work. Then change the default prioritizer to `lists` on the App Configuration object (or just on a particular user, depending on your desired setup). Once this is done the system will pull studies from the specified list (if specified at the user level, than the user list, if not, the global list). If you set the prioritization algorithm to `lists` but do not create and set any study lists, it will just pull from the database of eligible studies.

## Writing your own prioritizer

If you want to write a prioritizer yourself create a file called
`prioritizer.py` and place it in the root directory of the app. In the file, you create a function with the following signature


```python
def custom_algorithm(candidate_studies, user, annotation_class):
```

The first parameter is a django queryset of study objects that are eligible for review. The second is the user (django user object) currently reviewing studies, and the annotation_class is the is Django model that represents the review. Filter/order the candidate_studies in whatever way you would like and then return the modified queryset (or list).

Then, at the bottom of the file, place the following code

```python
from prioritizers import registry as prioritizers
prioritizers.register(custom_algorithm,"Name of Algorithm")
```

Your custom prioritizer will now be available in the Admin for use.

The `candidate_studies` parameter is a QuerySet of RadiologyStudy models. This model is declared in [here](https://github.com/cbmi/django-dicom-models/blob/master/dicom_models/staging/models.py#L69-L84) and inherits from this [model](https://github.com/cbmi/django-dicom-models/blob/master/dicom_models/core/models/data/radiology.py#L27-L33).

The `annotation_class` will be the django model defined [here](https://github.com/cbmi/django-dicom-models/blob/master/dicom_models/staging/models.py#L86-L94).

See [here](https://github.com/cbmi/django-dicom-review/blob/master/dicom_review/prioritizers.py#L9-L18) for examples of how to write a prioritizer.