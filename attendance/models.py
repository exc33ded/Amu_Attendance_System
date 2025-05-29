from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings  # Import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError


# Custom User Model with Role-Based Authentication
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser

# Custom User Model with Role-Based Authentication



from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('faculty', 'Faculty'),
        ('student', 'Student'),
        ('chairperson', 'Chairperson'),
        ('dean', 'Dean'),
        ('controller', 'Controller'),
    )
    
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='student')

    def __str__(self):
        return self.get_full_name() or self.username


# Department Model
class Department(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name



# Program Model
class Program(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    duration = models.IntegerField()  # Duration in Years
    num_semesters = models.IntegerField()  # Number of Semesters

    def __str__(self):
        return f"{self.name} ({self.department.name})"


# Semester Model (Each Program has Multiple Semesters)
class Semester(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="semesters")
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} ({self.program.name} - {self.program.department.name})"

    class Meta:
        unique_together = ('program', 'name')
        ordering = ['name']


# Automatically create semesters when a new program is added
@receiver(post_save, sender=Program)
def create_semesters_for_program(sender, instance, created, **kwargs):
    if created:
        for i in range(1, instance.num_semesters + 1):  # Create semesters based on program's `num_semesters`
            Semester.objects.create(name=f"Semester {i}", program=instance)


# Automatically delete semesters when a program is deleted
@receiver(pre_delete, sender=Program)
def delete_semesters_for_program(sender, instance, **kwargs):
    instance.semesters.all().delete()



#Course Model
class Course(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    code = models.CharField(max_length=20, unique=True)  # Course Code
    name = models.CharField(max_length=255)  # Course Name
    credit = models.IntegerField()  # Course Credit

    def __str__(self):
        return f"{self.code} - {self.name}"


# Teacher Model
class Teacher(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    teacher_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.teacher_code})"


from django.db import models

class Student(models.Model):
    enrollment_no = models.CharField(max_length=20, unique=True)  # Unique lifetime
    roll_no = models.CharField(max_length=20)  # Unique per session
    name = models.CharField(max_length=255)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    session = models.CharField(max_length=9)  # Format: 2024-2025

    class Meta:
        unique_together = ('roll_no', 'session', 'program', 'semester')  # Roll No unique per Session, Program, and Semester

    def __str__(self):
        return f"{self.name} ({self.enrollment_no}) - Roll No: {self.roll_no} ({self.session})"
    



from django.db import models
from attendance.models import Course, Department, Semester, Program
# from users.models import CustomUser  # Assuming CustomUser is your User model

class CourseTeacher(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'faculty'})
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    course = models.ManyToManyField(Course)  # Allow multiple courses



# New Model for Student Enrollment
# class EnrollStudent(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Student
#     department = models.ForeignKey(Department, on_delete=models.CASCADE)
#     program = models.ForeignKey(Program, on_delete=models.CASCADE)
#     semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
#     courses = models.ManyToManyField(Course, blank=True)  # Students can enroll in multiple or no courses

#     def __str__(self):
#         return f"{self.user.username} - {self.program.name} - {self.semester.name}"
    
from attendance.models import CustomUser  # Import CustomUser here
from django.db import models
from attendance.models import CustomUser  # Import CustomUser
from attendance.models import Department, Program, Semester, Course  # Ensure proper imports

class EnrollStudent(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='student')  # Link to CustomUser
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    courses = models.ManyToManyField(Course, blank=True)  # Students can enroll in multiple or no courses


    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Student Enrollment"
        verbose_name_plural = "Student Enrollments"





# Enrollment Model (Many-to-Many: Students <-> Courses)
class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrolled_students")

    def __str__(self):
        return f"{self.student.user.get_full_name()} enrolled in {self.course.name}"

    class Meta:
        unique_together = ('student', 'course')
        ordering = ['course']


# Attendance Model (Supports Date & Time)
class Attendance(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent')])
    marked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('course', 'student', 'date', 'marked_at')
        ordering = ['-date', '-marked_at']

    def __str__(self):
        return f"{self.student.name} - {self.course.name} - {self.date} - {self.status}"


@receiver(post_save, sender=CustomUser)
def set_superuser_role(sender, instance, created, **kwargs):
    if created and instance.is_superuser:
        instance.role = 'admin'
        instance.save()


class Chairperson(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    teacher_code = models.CharField(max_length=50, unique=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.department.name}"


class Dean(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dean - {self.teacher.name} ({self.department.name})"

    class Meta:
        verbose_name = "Dean"
        verbose_name_plural = "Deans"


User = get_user_model()

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('appointment', 'Appointment'),
        ('removal', 'Removal'),
        ('request', 'Request'),
        ('general', 'General'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255, null=True, blank=True)  # Make nullable
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='general', null=True, blank=True)  # Make nullable
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.email}: {self.title or self.message[:30]}"

    class Meta:
        ordering = ['-created_at']


class AttendanceChangeRequest(models.Model):
    faculty = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_change_requests', null=True, blank=True)
    student_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_attendance_change_requests', null=True, blank=True)
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    date = models.DateField()
    old_status = models.CharField(max_length=20)
    requested_status = models.CharField(max_length=20)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    decision = models.TextField(blank=True, null=True)
    
    def __str__(self):
        initiator = self.faculty.get_full_name() if self.faculty else self.student_user.get_full_name()
        return f"Request by {initiator} for {self.student.name} in {self.course.name} on {self.date}"
    
    def is_within_time_limit(self):
        """Check if request is within 1 hour of attendance marking"""
        try:
            attendance = Attendance.objects.get(
                student=self.student,
                course=self.course,
                date=self.date
            )
            time_diff = timezone.now() - attendance.marked_at
            return time_diff.total_seconds() <= 3600  # 1 hour in seconds
        except Attendance.DoesNotExist:
            return False


class ChairpersonRequest(models.Model):
    REQUEST_TYPES = (
        ('add', 'Add'),
        ('remove', 'Remove'),
        ('edit', 'Edit'),
    )
    
    REQUEST_STATUS = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    chairperson = models.ForeignKey(Chairperson, on_delete=models.CASCADE, related_name='requests')
    request_type = models.CharField(max_length=10, choices=REQUEST_TYPES)
    model_name = models.CharField(max_length=50)  # e.g., 'Department', 'Program', etc.
    object_id = models.IntegerField()  # ID of the object being modified
    changes = models.JSONField()  # Store the changes in JSON format
    status = models.CharField(max_length=10, choices=REQUEST_STATUS, default='pending')
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_by = models.ForeignKey(Dean, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_requests')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.chairperson.user.get_full_name()} - {self.request_type} {self.model_name}"

    class Meta:
        ordering = ['-created_at']


class Controller(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    department = models.ForeignKey('Department', on_delete=models.CASCADE)
    teacher = models.OneToOneField('Teacher', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Controller'
        verbose_name_plural = 'Controllers'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.department.name}"


class AdmitCardEligibility(models.Model):
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=75.00)
    last_modified = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.percentage}%"

    class Meta:
        verbose_name_plural = "Admit Card Eligibility"


class AdmitCardRequest(models.Model):
    REASON_CHOICES = [
        ('medical', 'Medical Issue'),
        ('family', 'Family Emergency'),
        ('technical', 'Technical Issue'),
        ('other', 'Other')
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField()
    proof_document = models.FileField(upload_to='admit_card_requests/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    relaxation_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    review_notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Admit Card Request - {self.student.name} ({self.get_status_display()})"



