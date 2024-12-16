from django.shortcuts import render
import companies
from rest_framework import viewsets
from rest_framework.views import APIView
from .serializers import *
from .models import *
from users.models import *
from users.helper import *
from systemrights.models import *
from systemrights.models import *
from rest_framework.response import Response
from kwani_api.utils import get_current_user
from rest_framework import status
from ledgers.helper import populate_system_coa

# Create your views here.


class StudyClassView(viewsets.ModelViewSet):
    serializer_class = StudyClassSerializer
    queryset = StudyClass.objects.all().order_by('-id')


class StreamCategoryView(viewsets.ModelViewSet):
    serializer_class = StreamCategorySerializer
    queryset = StreamCategory.objects.all().order_by('name')


class StreamView(viewsets.ModelViewSet):
    serializer_class = StreamSerializer

    def get_queryset(self):
        return Stream.objects.filter(parent=None).order_by('stream_category__name')


class SubjectCategoryView(viewsets.ModelViewSet):
    serializer_class = SubjectCategorySerializer
    queryset = SubjectCategory.objects.all().order_by('name')


class SubjectView(viewsets.ModelViewSet):
    serializer_class = SubjectSerializer
    queryset = Subject.objects.all().order_by('name')


class BranchSubjectCategoryView(viewsets.ModelViewSet):
    serializer_class = SubjectCategorySerializer

    def get_queryset(self):
        branch_id = get_current_user(self.request, 'branch_id', 1)
        if branch_id:
            return SubjectCategory.objects.filter(branch__id=branch_id).order_by('name')
        return SubjectCategory.objects.all().order_by('-id')

    def perform_create(self, serializer):
        branch_id = get_current_user(self.request, 'branch_id', 1)
        serializer.save(branch_id=branch_id, added_by=self.request.user)


class BranchSubjectView(viewsets.ModelViewSet):
    serializer_class = SubjectSerializer

    def get_queryset(self):
        branch_id = get_current_user(self.request, 'branch_id', 1)
        stream_id = self.request.query_params.get('stream_id', None)
        action = self.request.query_params.get('action', None)

        if branch_id:
            filter_query = {"branch__id": branch_id}

            if action == 'unassigned':
                subject_ids = StreamSubject.objects.filter(
                    stream__id=stream_id).values_list('subject__id', flat=True)
                return Subject.objects.filter(branch__id=branch_id).exclude(id__in=subject_ids).order_by('name')
            else:
                return Subject.objects.filter(**filter_query).order_by('name')
        return Subject.objects.all().order_by('-id')


class StudyYearView(viewsets.ModelViewSet):
    serializer_class = StudyYearSerializer

    def get_queryset(self):
        branch_id = get_current_user(self.request, 'branch_id', 1)
        if branch_id:
            return StudyYear.objects.filter(branch__id=branch_id).order_by('name')
        return StudyYear.objects.all().order_by('-id')

    def perform_create(self, serializer):
        branch_id = get_current_user(self.request, 'branch_id', 1)
        serializer.save(branch_id=branch_id, added_by=self.request.user)


class StudyPeriodView(viewsets.ModelViewSet):
    serializer_class = StudyPeriodSerializer

    def get_queryset(self):
        study_year_id = self.request.query_params.get('study_year', None)
        branch_id = get_current_user(self.request, 'branch_id', None)
        filter_list = {"study_year__branch__id": branch_id}

        if study_year_id:
            filter_list["study_year__id"] = study_year_id

        return StudyPeriod.objects.filter(**filter_list).order_by('name')

    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)


class ClassPeriodView(viewsets.ModelViewSet):
    serializer_class = ClassPeriodSerializer

    def get_queryset(self):
        branch_id = get_current_user(self.request, 'branch_id', 1)
        filter_list = {"study_period__study_year__branch__id": branch_id}
        study_year_id = self.request.query_params.get('study_year', None)
        study_period_id = self.request.query_params.get('study_period', None)

        if study_year_id:
            filter_list["study_period__study_year__id"] = study_year_id

        if study_period_id:
            filter_list["study_period__id"] = study_period_id

        return ClassPeriod.objects.filter(**filter_list).order_by('rank')


class ClassStreamView(viewsets.ModelViewSet):
    serializer_class = ClassStreamSerializer

    def get_queryset(self):
        branch_id = get_current_user(self.request, 'branch_id', 1)
        filter_list = {
            "class_period__study_period__study_year__branch__id": branch_id}
        class_period_id = self.request.query_params.get('class_period', None)
        study_period_id = self.request.query_params.get('study_period', None)

        if class_period_id:
            filter_list["class_period__id"] = class_period_id

        if study_period_id:
            filter_list["class_period__study_period__id"] = study_period_id

        return ClassStream.objects.filter(**filter_list).order_by('class_period__id')


class StreamStudentsView(viewsets.ModelViewSet):
    serializer_class = StreamStudentSerializer

    def get_queryset(self):
        branch_id = get_current_user(self.request, 'branch_id', 1)
        filter_list = {
            "stream__class_period__study_period__study_year__branch__id": branch_id}
        class_period_id = self.request.query_params.get('class_period', None)
        study_period_id = self.request.query_params.get('study_period', None)

        if class_period_id:
            filter_list["stream__class_period__id"] = class_period_id

        if study_period_id:
            filter_list["stream__class_period__study_period__id"] = study_period_id

        return StreamStudent.objects.filter(**filter_list).order_by('stream__name')


class StreamSubjectsView(viewsets.ModelViewSet):
    serializer_class = StreamSubjectSerializer

    def get_queryset(self):
        branch_id = get_current_user(self.request, 'branch_id', 1)
        filter_list = {
            "stream__class_period__study_period__study_year__branch__id": branch_id}
        stream_id = self.request.query_params.get('stream_id', None)
        study_period_id = self.request.query_params.get('study_period', None)

        if stream_id:
            filter_list["stream__id"] = stream_id

        if study_period_id:
            filter_list["stream__class_period__study_period__id"] = study_period_id

        return StreamSubject.objects.filter(**filter_list).order_by('stream__name')


class SubjectTeacherView(viewsets.ModelViewSet):
    serializer_class = SubjectTeacherSerializer

    def get_queryset(self):
        branch_id = get_current_user(self.request, 'branch_id', 1)
        filter_list = {
            "subject_stream__class_period__study_period__study_year__branch__id": branch_id}
        stream_id = self.request.query_params.get('stream_id', None)
        study_period_id = self.request.query_params.get('study_period', None)

        if stream_id:
            filter_list["subject__id"] = stream_id

        if study_period_id:
            filter_list["subject_stream__class_period__study_period__id"] = study_period_id

        return SubjectTeacher.objects.filter(**filter_list).order_by('stream__name')


class GradeRuleView(viewsets.ModelViewSet):
    serializer_class = GradeRuleSerializer

    def get_queryset(self):
        branch_id = get_current_user(self.request, 'branch_id', 1)
        filter_list = {
            "class_period__study_period__study_year__branch__id": branch_id}
        class_period_id = self.request.query_params.get('class_period', None)
        study_period_id = self.request.query_params.get('study_period', None)

        if class_period_id:
            filter_list["class_period__id"] = class_period_id

        if study_period_id:
            filter_list["class_period__study_period__id"] = study_period_id

        return GradeRule.objects.filter(**filter_list).order_by('rank')


class GradeWeightView(viewsets.ModelViewSet):
    serializer_class = GradeWeightSerializer

    def get_queryset(self):
        branch_id = get_current_user(self.request, 'branch_id', 1)
        filter_list = {
            "class_period__study_period__study_year__branch__id": branch_id}
        class_period_id = self.request.query_params.get('class_period', None)
        study_period_id = self.request.query_params.get('study_period', None)

        if class_period_id:
            filter_list["class_period__id"] = class_period_id

        if study_period_id:
            filter_list["class_period__study_period__id"] = study_period_id

        return GradeWeight.objects.filter(**filter_list).order_by('rank')


class AssessmentTypeView(viewsets.ModelViewSet):
    serializer_class = AssessmentTypeSerializer

    def get_queryset(self):
        branch_id = get_current_user(self.request, 'branch_id', 1)
        filter_list = {"branch__id": branch_id}

        return AssessmentType.objects.filter(**filter_list).order_by('rank')

    def perform_create(self, serializer):
        branch_id = get_current_user(self.request, 'branch_id', 1)
        serializer.save(branch_id=branch_id, added_by=self.request.user)


class AssessmentView(viewsets.ModelViewSet):
    serializer_class = AssessmentSerializer

    def get_queryset(self):
        branch_id = get_current_user(self.request, 'branch_id', 1)
        filter_list = {
            "class_period__study_period__study_year__branch__id": branch_id}
        class_period_id = self.request.query_params.get('class_period', None)
        study_period_id = self.request.query_params.get('study_period', None)

        if class_period_id:
            filter_list["class_period__id"] = class_period_id

        if study_period_id:
            filter_list["class_period__study_period__id"] = study_period_id

        return Assessment.objects.filter(**filter_list).order_by('rank')


class NewClassPeriodsApiView(APIView):

    def post(self, request, format=None):
        class_list = self.request.data.get('class_list', [])
        study_period = self.request.data.get('study_period', None)

        if len(class_list) > 0:
            study_classes = StudyClass.objects.filter(id__in=class_list)
            if study_classes:
                for study_class in study_classes:
                    classperiod = ClassPeriod.objects.filter(
                        study_period__id=study_period, study_class=study_class)
                    if not classperiod:
                        ClassPeriod.objects.create(**{
                            "name": study_class.name,
                            "abbr": study_class.abbr,
                            "rank": study_class.rank,
                            "study_period_id": study_period,
                            "study_class": study_class,
                            "added_by": self.request.user
                        })
                return Response({"status": "success", "message": "successful message"}, status=status.HTTP_200_OK)

        return Response({"status": "failed", "message": "Failed to register classes"}, status=status.HTTP_200_OK)


class NewClassStreamsApiView(APIView):

    def post(self, request, format=None):
        stream_list = self.request.data.get('stream_list', [])
        classperiod = self.request.data.get('classperiod', None)

        if len(stream_list) > 0:
            streams = Stream.objects.filter(id__in=stream_list)
            if streams:
                for stream in streams:
                    class_stream = ClassStream.objects.filter(
                        class_period__id=classperiod, stream=stream)
                    if not class_stream:
                        ClassStream.objects.create(**{
                            "name": stream.name,
                            "stream": stream,
                            "class_period_id": classperiod,
                            "added_by": self.request.user
                        })
                return Response({"status": "success", "message": "successful message"}, status=status.HTTP_200_OK)

        return Response({"status": "failed", "message": "Failed to register streams"}, status=status.HTTP_200_OK)


class NewGradeRulesApiView(APIView):

    def post(self, request, format=None):
        grade_list = self.request.data.get('grade_list', [])
        classperiod = self.request.data.get('classperiod', None)

        if len(grade_list) > 0:
            grades = GradeRule.objects.filter(id__in=grade_list)
            if grades:
                for grade in grades:
                    class_grade = GradeRule.objects.filter(
                        class_period__id=classperiod, symbol=grade.symbol)
                    if not class_grade:
                        GradeRule.objects.create(**{
                            "symbol": grade.symbol,
                            "min_grade": grade.min_grade,
                            "max_grade": grade.max_grade,
                            "comment": grade.comment,
                            "rank": grade.rank,
                            "class_period_id": classperiod,
                            "added_by": self.request.user
                        })
                return Response({"status": "success", "message": "successful message"}, status=status.HTTP_200_OK)

        return Response({"status": "failed", "message": "Failed to register streams"}, status=status.HTTP_200_OK)


class NewGradeWeightApiView(APIView):

    def post(self, request, format=None):
        grade_list = self.request.data.get('grade_list', [])
        classperiod = self.request.data.get('classperiod', None)

        if len(grade_list) > 0:
            grades = GradeWeight.objects.filter(id__in=grade_list)
            if grades:
                for grade in grades:
                    class_grade = GradeWeight.objects.filter(
                        class_period__id=classperiod, symbol=grade.symbol)
                    if not class_grade:
                        GradeWeight.objects.create(**{
                            "symbol": grade.symbol,
                            "weight": grade.weight,
                            "min_weight": grade.min_weight,
                            "max_weight": grade.max_weight,
                            "comment": grade.comment,
                            "rank": grade.rank,
                            "class_period_id": classperiod,
                            "added_by": self.request.user
                        })
                return Response({"status": "success", "message": "successful message"}, status=status.HTTP_200_OK)

        return Response({"status": "failed", "message": "Failed to register streams"}, status=status.HTTP_200_OK)


class NewSubjectApiView(APIView):

    def post(self, request, format=None):
        subject_list = self.request.data.get('subject_list', [])
        branch_id = get_current_user(self.request, 'branch_id', 1)

        if len(subject_list) > 0:
            subjects = Subject.objects.filter(id__in=subject_list)
            if subjects:
                for subject in subjects:
                    assigned_subject = Subject.objects.filter(
                        branch__id=branch_id, parent=subject)
                    if not assigned_subject:
                        Subject.objects.create(**{
                            "name": subject.name,
                            "abbr": subject.abbr,
                            "section": subject.section,
                            "branch_id": branch_id,
                            "parent": subject,
                            "added_by": self.request.user
                        })
                return Response({"status": "success", "message": "successful Added"}, status=status.HTTP_200_OK)

        return Response({"status": "failed", "message": "Failed to register subjects"}, status=status.HTTP_200_OK)


class NewStreamSubjectApiView(APIView):

    def post(self, request, format=None):
        subject_list = self.request.data.get('subject_list', [])
        stream_id = self.request.data.get('stream', None)
        if len(subject_list) > 0:
            subjects = Subject.objects.filter(id__in=subject_list)
            if subjects:
                for subject in subjects:
                    assigned_subject = StreamSubject.objects.filter(
                        subject=subject, stream__id=stream_id)
                    if not assigned_subject:
                        StreamSubject.objects.create(**{
                            "subject": subject,
                            "stream_id": stream_id,
                            "added_by": self.request.user
                        })
                return Response({"status": "success", "message": "successfully Added"}, status=status.HTTP_200_OK)

        return Response({"status": "failed", "message": "Failed to register subjects"}, status=status.HTTP_200_OK)


class NewSubjectTeacherApiView(APIView):

    def get(self, request, format=None):
        '''
        Get transactions
        '''
        teachers = []
        subject_id = request.GET.get('subject_id', None)
        action = request.GET.get('action', None)
        branch_id = get_current_user(self.request, 'branch_id', None)

        if action == 'unassigned':
           assigned_teacher_ids = SubjectTeacher.objects.filter(
               subject__id=subject_id).values_list('teacher__id', flat=True)
                      
           teacher_id_list = StaffAssignedDepartment.objects.filter(department__branch=branch_id).values_list('staff__user__id',flat=True)
           teacher_list = User.objects.filter(id__in=teacher_id_list).filter(id__in=teacher_id_list).order_by('first_name')
           teachers = UserSerializer(teacher_list, many=True).data
        data = {
            'count': len(teachers),
            'results': teachers
        }

        return Response(data, status=status.HTTP_200_OK)


    def post(self, request, format=None):
        subject_list   = self.request.data.get('subject_list', [])  
        teacher_id = self.request.data.get('teacher',None)  
        
        if len(subject_list) > 0:
            subjects = StreamSubject.objects.filter(id__in=subject_list)
            if subjects:
                for subject in subjects:
                    assigned_teacher = SubjectTeacher.objects.filter(subject=subject,teacher__id=teacher_id)
                    if not assigned_teacher:
                        SubjectTeacher.objects.create(**{
                            "subject":subject,
                            "teacher_id":teacher_id,
                            "added_by":self.request.user
                        })
                return Response({"status":"success","message":"successfully Added"}, status=status.HTTP_200_OK)
    
        return Response({"status":"failed","message":"Failed to register subjects"}, status=status.HTTP_200_OK)
    
