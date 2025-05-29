from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Department, Program, Semester, Teacher, Student, Course, Enrollment, Attendance, Chairperson, EnrollStudent, AttendanceChangeRequest, AdmitCardRequest
from django.utils import timezone

# Custom User Registration Form with Role Selection
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser  # Ensure CustomUser model is imported

# from django import forms
# from django.contrib.auth.forms import UserCreationForm
# from .models import CustomUser

# class CustomUserCreationForm(UserCreationForm):
#     role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, label="User Role")

#     class Meta:
#         model = CustomUser
#         fields = ['username', 'first_name', 'last_name', 'email', 'role', 'password1', 'password2']

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=CustomUser.ROLE_CHOICES, label="User Role")

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'password1', 'password2')


# Department Form
class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name']

# Program Form (Dropdown for Department)
from django import forms
from .models import Program, Department

class ProgramForm(forms.ModelForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),  # Fetch all departments
        empty_label="Select Department",
        widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = Program
        fields = ["department", "name"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter program name"}),
        }


# Semester Form (Dropdown for Program)
class SemesterForm(forms.ModelForm):
    class Meta:
        model = Semester
        fields = ['program', 'name']




from django import forms
from .models import Course

from django import forms
from .models import Course

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['department', 'program', 'semester', 'code', 'name', 'credit']


# Teacher Registration Form
from django import forms
from .models import Teacher, Department, CustomUser  # Import CustomUser

class TeacherForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role = "faculty"),  # Use CustomUser instead of User
        empty_label="Select a User",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        empty_label="Select Department",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

from django import forms
from .models import CourseTeacher, CustomUser, Course, Department, Program, Semester
from django import forms
from .models import CourseTeacher, CustomUser, Course, Department, Program, Semester

class AssignTeacherForm(forms.ModelForm):
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=True, label="Select Department")
    program = forms.ModelChoiceField(queryset=Program.objects.all(), required=True, label="Select Program")
    semester = forms.ModelChoiceField(queryset=Semester.objects.all(), required=True, label="Select Semester")
    course = forms.ModelMultipleChoiceField(queryset=Course.objects.all(), widget=forms.CheckboxSelectMultiple, required=True, label="Select Courses")  # ✅ Allow multiple courses
    user = forms.ModelChoiceField(queryset=CustomUser.objects.filter(role="faculty"), label="Select Teacher")

    class Meta:
        model = CourseTeacher
        fields = ['user', 'department', 'program', 'semester', 'course']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'department' in self.data:
            try:
                department_id = int(self.data.get('department'))
                self.fields['program'].queryset = Program.objects.filter(department_id=department_id)
            except (ValueError, TypeError):
                self.fields['program'].queryset = Program.objects.none()

        if 'program' in self.data:
            try:
                program_id = int(self.data.get('program'))
                self.fields['semester'].queryset = Semester.objects.filter(program_id=program_id)
            except (ValueError, TypeError):
                self.fields['semester'].queryset = Semester.objects.none()

        if 'semester' in self.data:
            try:
                semester_id = int(self.data.get('semester'))
                self.fields['course'].queryset = Course.objects.filter(semester_id=semester_id)
            except (ValueError, TypeError):
                self.fields['course'].queryset = Course.objects.none()



from django import forms
from .models import Student

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['enrollment_no', 'roll_no', 'name', 'department', 'program', 'semester', 'session']  # Added 'session'
        widgets = {
            'department': forms.Select(attrs={'class': 'form-control'}),
            'program': forms.Select(attrs={'class': 'form-control'}),
            'semester': forms.Select(attrs={'class': 'form-control'}),
            'session': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2024-2025'}),  # Added session widget
        }

# Enrollment Form (Assign Student to a Course)
class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student', 'course']

# Attendance Form (Mark Attendance for Students)
class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['course', 'student', 'date', 'status']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }






from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class TeacherRegistrationForm(UserCreationForm):
    teacher_code = forms.CharField(max_length=50, required=True)
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        empty_label="Select Department",
        required=True
    )
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'teacher_code', 'department', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'faculty'
        if commit:
            user.save()
            # Create Teacher profile
            Teacher.objects.create(
                user=user,
                teacher_code=self.cleaned_data['teacher_code'],
                department=self.cleaned_data['department']
            )
        return user







# ----------------------------------------------------------Student Registration form 25 March -------------------------
# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, EnrollStudent

class StudentRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    enrollment_no = forms.CharField(max_length=20, required=True)
    roll_no = forms.CharField(max_length=20, required=True)
    mobile_no = forms.CharField(max_length=15, required=True)
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        empty_label="Select Department",
        required=True
    )
    program = forms.ModelChoiceField(
        queryset=Program.objects.none(),
        empty_label="Select Program",
        required=True
    )
    semester = forms.ModelChoiceField(
        queryset=Semester.objects.none(),
        empty_label="Select Semester",
        required=True
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'enrollment_no', 'roll_no', 'mobile_no', 
                 'department', 'program', 'semester', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'department' in self.data:
            try:
                department_id = int(self.data.get('department'))
                self.fields['program'].queryset = Program.objects.filter(department_id=department_id)
            except (ValueError, TypeError):
                self.fields['program'].queryset = Program.objects.none()

        if 'program' in self.data:
            try:
                program_id = int(self.data.get('program'))
                self.fields['semester'].queryset = Semester.objects.filter(program_id=program_id)
            except (ValueError, TypeError):
                self.fields['semester'].queryset = Semester.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        enrollment_no = cleaned_data.get('enrollment_no')

        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered!")

        if Student.objects.filter(enrollment_no=enrollment_no).exists():
            raise forms.ValidationError("Enrollment number already exists!")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'student'
        user.username = self.cleaned_data['enrollment_no']
        if commit:
            user.save()
            Student.objects.create(
                user=user,
                enrollment_no=self.cleaned_data['enrollment_no'],
                roll_no=self.cleaned_data['roll_no'],
                name=f"{self.cleaned_data['first_name']} {self.cleaned_data['last_name']}",
                department=self.cleaned_data['department'],
                program=self.cleaned_data['program'],
                semester=self.cleaned_data['semester'],
                session=f"{timezone.now().year}-{timezone.now().year + 1}"
            )
        return user

class StudentEnrollForm(forms.ModelForm):
    class Meta:
        model = EnrollStudent
        fields = ['department', 'program', 'semester', 'courses']
        widgets = {
            'courses': forms.CheckboxSelectMultiple()
        }

class AdminRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "admin"
        if commit:
            user.save()
        return user

class ChairpersonRegistrationForm(UserCreationForm):
    teacher_code = forms.CharField(max_length=50, required=True)
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        empty_label="Select Department",
        required=True
    )
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'teacher_code', 'department', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Use email as username
        user.role = 'chairperson'
        if commit:
            user.save()
            # Create Chairperson profile
            Chairperson.objects.create(
                user=user,
                teacher_code=self.cleaned_data['teacher_code'],
                department=self.cleaned_data['department']
            )
        return user

class AttendanceChangeRequestForm(forms.ModelForm):
    ATTENDANCE_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent')
    ]

    REASON_CHOICES = [
        ('Medical Emergency', 'Medical Emergency'),
        ('Technical Issue', 'Technical Issue'),
        ('Late Attendance', 'Late Attendance'),
        ('Administrative Error', 'Administrative Error'),
        ('Other', 'Other')
    ]

    course = forms.ModelChoiceField(queryset=Course.objects.none())
    student = forms.ModelChoiceField(queryset=Student.objects.none())
    old_status = forms.ChoiceField(choices=ATTENDANCE_CHOICES, disabled=True)
    requested_status = forms.ChoiceField(choices=ATTENDANCE_CHOICES)
    reason = forms.ChoiceField(choices=REASON_CHOICES)
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = AttendanceChangeRequest
        fields = ['course', 'student', 'date', 'old_status', 'requested_status', 'reason']

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['course'].queryset = Course.objects.filter(
                courseteacher__user=user
            ).distinct()
            self.fields['student'].queryset = Student.objects.filter(
                attendance__course__in=self.fields['course'].queryset
            ).distinct()

class StudentAttendanceChangeRequestForm(forms.ModelForm):
    REASON_CHOICES = [
        ('Medical Emergency', 'Medical Emergency'),
        ('Technical Issue', 'Technical Issue'),
        ('Late Attendance', 'Late Attendance'),
        ('Administrative Error', 'Administrative Error'),
        ('Other', 'Other')
    ]

    reason = forms.ChoiceField(choices=REASON_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    additional_details = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), required=False)

    class Meta:
        model = AttendanceChangeRequest
        fields = ['reason']

    def __init__(self, *args, **kwargs):
        self.attendance_id = kwargs.pop('attendance_id', None)
        super().__init__(*args, **kwargs)

class AdmitCardRequestForm(forms.ModelForm):
    class Meta:
        model = AdmitCardRequest
        fields = ['reason', 'description', 'proof_document']
        widgets = {
            'reason': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'proof_document': forms.FileInput(attrs={'class': 'form-control'})
        }
