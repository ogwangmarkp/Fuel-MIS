from django.db import models
from django.utils import timezone
from companies.models import CompanyBranch, Company
from customers.models import Customer
from django.conf import settings


class StudyClass(models.Model):
    SECTIONS = (
        ('O Level', 'O Level'),
        ('A Level', 'A Level'), 
        ('Primary', 'Primary'),
        ('Nursery', 'Nursery')
    )
    name = models.CharField(max_length=100)
    abbr = models.CharField(max_length=100)
    rank    = models.IntegerField(null=True)
    section = models.CharField(max_length=100,choices=SECTIONS,null=True,blank=True)
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='study_class_added_by', null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'public\".\"study_class'


class StreamCategory(models.Model):
    name = models.CharField(max_length=100)
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='stream_category_added_by', null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'public\".\"stream_category'


class Stream(models.Model):
    name = models.CharField(max_length=100)
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='stream_added_by', null=True, blank=True)
    stream_category = models.ForeignKey(
        StreamCategory, on_delete=models.CASCADE, related_name='stream_stream_category')
    parent = models.ForeignKey(
        'Stream', on_delete=models.CASCADE, related_name='parent_stream', null=True, blank=True)

    class Meta:
        db_table = 'public\".\"stream'


class SubjectCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='subject_category_added_by', null=True, blank=True)
    branch = models.ForeignKey(
        CompanyBranch, on_delete=models.CASCADE, related_name='sub_cat_branch', null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'public\".\"subject_category'


class Subject(models.Model):
    SECTIONS = (
        ('O Level', 'O Level'),
        ('A Level', 'A Level'), 
        ('Primary', 'Primary'),
        ('Nursery', 'Nursery')
    )
    name = models.CharField(max_length=100)
    abbr = models.CharField(max_length=100)
    section = models.CharField(max_length=100,choices=SECTIONS,null=True,blank=True)
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='subject_added_by', null=True, blank=True)
    sub_category = models.ForeignKey(
        SubjectCategory, on_delete=models.CASCADE, related_name='subject_sub_cat', null=True, blank=True)
    parent = models.ForeignKey(
        'Subject', on_delete=models.CASCADE, related_name='parent_subject', null=True, blank=True)
    
    branch = models.ForeignKey(
        CompanyBranch, on_delete=models.CASCADE, related_name='sub_branch', null=True, blank=True)
    
    class Meta:
        db_table = 'public\".\"subject'


class SubjectDepartment(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='subject_dept_added_by', null=True, blank=True)
    department = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='subject_dept')

    class Meta:
        db_table = 'public\".\"subject_department'


class StudyYear(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='study_year_added_by', null=True, blank=True)
    last_updated = models.DateTimeField(default=timezone.now)
    last_updated_by = models.BigIntegerField(null=True, blank=True)
    branch = models.ForeignKey(
        CompanyBranch, on_delete=models.CASCADE, related_name='study_year_company_branch')

    class Meta:
        db_table = 'public\".\"study_year'


class StudyPeriod(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    open_date = models.DateTimeField(null=True, blank=True)
    is_promo = models.BooleanField(default=False)
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='study_period_added_by', null=True, blank=True)
    last_updated = models.DateTimeField(default=timezone.now)
    last_updated_by = models.BigIntegerField(null=True, blank=True)
    study_year = models.ForeignKey(
        StudyYear, on_delete=models.CASCADE, related_name='period_study_year')

    class Meta:
        db_table = 'public\".\"study_period'


class ClassPeriod(models.Model):
    name  = models.CharField(max_length=100)
    abbr  = models.CharField(max_length=100)
    rank  = models.IntegerField(null=True)
    has_stream = models.BooleanField(default=False)
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='class_period_added_by', null=True, blank=True)
    last_updated = models.DateTimeField(default=timezone.now)
    last_updated_by = models.BigIntegerField(null=True, blank=True)
    study_period = models.ForeignKey(
        StudyPeriod, on_delete=models.CASCADE, related_name='class_period_study_period')
    study_class = models.ForeignKey(
        StudyClass, on_delete=models.CASCADE, related_name='class_period_class')
    class_teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='class_teacher', null=True, blank=True)

    class Meta:
        db_table = 'public\".\"class_period'


class ClassStream(models.Model):
    name = models.CharField(max_length=100)
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='class_stream_added_by', null=True, blank=True)
    stream = models.ForeignKey(
        Stream, on_delete=models.CASCADE, related_name='class_stream_stm')
    class_period = models.ForeignKey(
        ClassPeriod, on_delete=models.CASCADE, related_name='class_stream_clp')

    class Meta:
        db_table = 'public\".\"class_stream'


class StreamStudent(models.Model):
    section = models.CharField(max_length=100,null=True,blank=True,default='Day')
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='stream_student_added_by', null=True, blank=True)
    stream = models.ForeignKey(
        ClassStream, on_delete=models.CASCADE, related_name='student_strm')
    student = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='strm_student')

    class Meta:
        db_table = 'public\".\"stream_student'


class StreamSubject(models.Model):
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='stream_suject_added_by', null=True, blank=True)
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name='stream_subj')
    stream = models.ForeignKey(
        ClassStream, on_delete=models.CASCADE, related_name='stream_subject_strm')
    is_compulsory = models.BooleanField(default=False)
    class Meta:
        db_table = 'public\".\"stream_subject'


class StudentSubject(models.Model):
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='student_suject_added_by', null=True, blank=True)
    subject = models.ForeignKey(
        StreamSubject, on_delete=models.CASCADE, related_name='student_subject')
    student = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='subj_student')

    class Meta:
        db_table = 'public\".\"student_subject'


class SubjectTeacher(models.Model):
    is_active = models.BooleanField(default=True)
    is_main = models.BooleanField(default=False)
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='suject_teacher_added_by', null=True, blank=True)
    subject = models.ForeignKey(
        StreamSubject, on_delete=models.CASCADE, related_name='suject_teacher_subj')
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='stream_suject_teacher', null=True, blank=True)

    class Meta:
        db_table = 'public\".\"subject_teacher'

class GradeRule(models.Model):
    symbol = models.CharField(max_length=100)
    min_grade = models.FloatField(default=0.0)
    max_grade = models.FloatField(default=0.0)
    rank      = models.IntegerField(default=0)
    comment   = models.CharField(max_length=100)
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='grade_rule_added_by', null=True, blank=True)
    class_period = models.ForeignKey(
        ClassPeriod, on_delete=models.CASCADE, related_name='grade_rule_clp')

    class Meta:
        db_table = 'public\".\"grade_rule'

class GradeWeight(models.Model):
    symbol = models.CharField(max_length=100)
    weight = models.FloatField(default=0.0)
    min_weight = models.FloatField(default=0.0)
    max_weight = models.FloatField(default=0.0)
    rank       = models.IntegerField(default=0)
    comment    = models.CharField(max_length=100)
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='grade_weight_added_by', null=True, blank=True)
    class_period = models.ForeignKey(
        ClassPeriod, on_delete=models.CASCADE, related_name='grade_weight_clp')

    class Meta:
        db_table = 'public\".\"grade_weight'

class AssessmentType(models.Model):
    name = models.CharField(max_length=100)
    abbr = models.CharField(max_length=100)
    rank    = models.IntegerField(null=True)
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='assessment_type_added_by', null=True, blank=True)
    branch = models.ForeignKey(CompanyBranch, on_delete=models.CASCADE, related_name='assessment_type_branch')
    
    class Meta:
        db_table = 'public\".\"assessment_type'

class Assessment(models.Model):
    contribution = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='assessment_added_by', null=True, blank=True)
    assessment_type = models.ForeignKey(AssessmentType, on_delete=models.CASCADE, related_name='assessment_assessment_type')
    
    class_period = models.ForeignKey(
        ClassPeriod, on_delete=models.CASCADE, related_name='assessment_clp')
    
    class Meta:
        db_table = 'public\".\"assessment'