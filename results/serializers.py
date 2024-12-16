from rest_framework import serializers
from .models import *
from customers.serializers import CustomerSerializer
from users.serializers import UserSerializer

class StudyClassSerializer(serializers.ModelSerializer):
    
    def __str__(self):
        return self.name 
     
    class Meta:
        model = StudyClass
        fields = '__all__'

class StreamCategorySerializer(serializers.ModelSerializer):
    
    def __str__(self):
        return self.name 
     
    class Meta:
        model = StreamCategory
        fields = '__all__'
        
class StreamSerializer(serializers.ModelSerializer):
    stream_cat_name = serializers.CharField(read_only=True,source='stream_category.name')

    def __str__(self):
        return self.name 
     
    class Meta:
        model = Stream
        fields = '__all__'

class SubjectCategorySerializer(serializers.ModelSerializer):
    
    def __str__(self):
        return self.name 
     
    class Meta:
        model = SubjectCategory
        fields = '__all__'

class SubjectSerializer(serializers.ModelSerializer):
    sub_category_name = serializers.CharField(read_only=True,source='sub_category.name')

    def __str__(self):
        return self.name 
     
    class Meta:
        model = Subject
        fields = '__all__'


class StudyYearSerializer(serializers.ModelSerializer):
    branch = serializers.CharField(read_only=True)

    def __str__(self):
        return self.name 
     
    class Meta:
        model = StudyYear
        fields = '__all__'

class StudyPeriodSerializer(serializers.ModelSerializer):
    study_year_name = serializers.CharField(read_only=True,source='study_year.name')

    def __str__(self):
        return self.name 
     
    class Meta:
        model = StudyPeriod
        fields = '__all__'

class ClassPeriodSerializer(serializers.ModelSerializer):
    study_period_name = serializers.CharField(read_only=True,source='study_period.name')
    
    def __str__(self):
        return self.name 
     
    class Meta:
        model = ClassPeriod
        fields = '__all__'



class ClassStreamSerializer(serializers.ModelSerializer):
    study_period_id = serializers.CharField(read_only=True,source='class_period.study_period.id')
    study_period_name = serializers.CharField(read_only=True,source='class_period.study_period.name')
    class_name = serializers.CharField(read_only=True,source='class_period.name')
    class_abbr = serializers.CharField(read_only=True,source='class_period.abbr')
    stream_cat = serializers.CharField(read_only=True,source='stream.stream_category.name')
    def __str__(self):
        return self.name 
     
    class Meta:
        model = ClassStream
        fields = '__all__'


class StreamStudentSerializer(serializers.ModelSerializer):
    stream_details = serializers.SerializerMethodField(read_only=True)
    student_details = serializers.SerializerMethodField(read_only=True)

    def get_stream_details(self, student_stream):
        return ClassStreamSerializer(student_stream.stream).data
   
    def get_student_details(self, student_stream):
        return CustomerSerializer(student_stream.student).data
    
    class Meta:
        model = StreamStudent
        fields = '__all__'
    
class StreamSubjectSerializer(serializers.ModelSerializer):
    stream_details = serializers.SerializerMethodField(read_only=True)
    subject_details = serializers.SerializerMethodField(read_only=True)

    def get_stream_details(self, stream_subject):
        return ClassStreamSerializer(stream_subject.stream).data
   
    def get_subject_details(self, stream_subject):
        return SubjectSerializer(stream_subject.subject).data
   
    class Meta:
        model = StreamSubject
        fields = '__all__'

class StreamSubjectSerializer(serializers.ModelSerializer):
    stream_details = serializers.SerializerMethodField(read_only=True)
    subject_details = serializers.SerializerMethodField(read_only=True)
    subject_teachers = serializers.SerializerMethodField(read_only=True)

    def get_stream_details(self, stream_subject):
        return ClassStreamSerializer(stream_subject.stream).data
   
    def get_subject_details(self, stream_subject):
        return SubjectSerializer(stream_subject.subject).data
    
    def get_subject_teachers(self, stream_subject):
        subject_teachers = SubjectTeacher.objects.filter(subject=stream_subject)
        return SubjectTeacherSerializer(subject_teachers,many=True).data
    
    class Meta:
        model = StreamSubject
        fields = '__all__'


class SubjectTeacherSerializer(serializers.ModelSerializer):
    teacher_details = serializers.SerializerMethodField(read_only=True)

    def get_teacher_details(self, subject_teacher):
        return UserSerializer(subject_teacher.teacher).data
   
    class Meta:
        model = SubjectTeacher
        fields = '__all__'


class GradeRuleSerializer(serializers.ModelSerializer):
    study_period_id = serializers.CharField(read_only=True,source='class_period.study_period.id')
    study_period_name = serializers.CharField(read_only=True,source='class_period.study_period.name')
    class_name = serializers.CharField(read_only=True,source='class_period.name')
    class_abbr = serializers.CharField(read_only=True,source='class_period.abbr')
    def __str__(self):
        return self.symbol 
     
    class Meta:
        model = GradeRule
        fields = '__all__'

class GradeWeightSerializer(serializers.ModelSerializer):
    study_period_id = serializers.CharField(read_only=True,source='class_period.study_period.id')
    study_period_name = serializers.CharField(read_only=True,source='class_period.study_period.name')
    class_name = serializers.CharField(read_only=True,source='class_period.name')
    class_abbr = serializers.CharField(read_only=True,source='class_period.abbr')
    def __str__(self):
        return self.symbol 
     
    class Meta:
        model = GradeWeight
        fields = '__all__'

class AssessmentTypeSerializer(serializers.ModelSerializer):
    branch = serializers.CharField(read_only=True)

    def __str__(self):
        return self.name 
     
    class Meta:
        model = AssessmentType
        fields = '__all__'

class AssessmentSerializer(serializers.ModelSerializer):
    study_period_id = serializers.CharField(read_only=True,source='class_period.study_period.id')
    study_period_name = serializers.CharField(read_only=True,source='class_period.study_period.name')
    class_name = serializers.CharField(read_only=True,source='class_period.name')
    class_abbr = serializers.CharField(read_only=True,source='class_period.abbr')
    assessment_type_name = serializers.CharField(read_only=True,source="assessment_type.name")

    def __str__(self):
        return self.contribution 
     
    class Meta:
        model = Assessment
        fields = '__all__'
