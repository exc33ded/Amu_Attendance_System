from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Department, Program, Semester, Teacher, Student, Course, Enrollment, Attendance, Chairperson, EnrollStudent, AttendanceChangeRequest
from django.utils import timezone

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