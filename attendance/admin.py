from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Department, Program, Semester, Teacher, Student, Course, Enrollment, Attendance, CourseTeacher

# Custom User Admin with Role-Based Authentication
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'first_name', 'last_name', 'email', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    fieldsets = UserAdmin.fieldsets + (
        ('User Role', {'fields': ('role',)}),
    )





from django.contrib import admin
from .models import EnrollStudent

class EnrollStudentAdmin(admin.ModelAdmin):
    # Display fields in the list view
    list_display = ('user', 'department', 'program', 'semester', 'get_courses')

    # Add search functionality for certain fields
    search_fields = ['user__username', 'department__name', 'program__name', 'semester__name']

    # Add filters for better navigation
    list_filter = ('department', 'program', 'semester')

    # Allow courses to be displayed as a comma-separated list
    def get_courses(self, obj):
        return ", ".join([course.name for course in obj.courses.all()])
    get_courses.short_description = 'Courses'

    # Optional: Add the `user` field to the "Add" and "Edit" form to allow selection of students
    fields = ('user', 'department', 'program', 'semester', 'courses')

    # Optional: Make the `courses` field a multi-select field
    filter_horizontal = ('courses',)

# Register the EnrollStudent model with the custom admin interface
admin.site.register(EnrollStudent, EnrollStudentAdmin)


# Department Admin
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

# Program Admin
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('name', 'department')
    list_filter = ('department',)
    search_fields = ('name',)

# Semester Admin
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('name', 'program')
    list_filter = ('program',)
    search_fields = ('name',)


from django.contrib import admin
from .models import Course


class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'credit', 'department', 'program', 'semester')
    search_fields = ('name', 'code')


# Teacher Admin
from django.contrib import admin
from .models import Teacher

class TeacherAdmin(admin.ModelAdmin):
    list_display = ('teacher_code', 'name', 'department')  # Ensure these fields exist
    list_filter = ('department',)  # Filter teachers by department
    search_fields = ('teacher_code', 'name')  # Allow search by teacher_code and name
    ordering = ('department', 'name')  # Order by department, then name




# Student Admin

# class StudentAdmin(admin.ModelAdmin):
#     list_display = ('enrollment_no', 'roll_no', 'name', 'department', 'program', 'semester')
#     list_filter = ('department', 'program', 'semester')
#     search_fields = ('enrollment_no', 'name', 'roll_no')
#     ordering = ('name',)
#     # list_per_page = 20


from django.contrib import admin
from .models import Student

class StudentAdmin(admin.ModelAdmin):
    list_display = ('enrollment_no', 'roll_no', 'name', 'department', 'program', 'semester', 'session')
    list_filter = ('department', 'program', 'semester', 'session')
    search_fields = ('enrollment_no', 'name', 'roll_no', 'session')
    ordering = ('name',)
    list_per_page = 20  # Optional: Paginate admin list view

# admin.site.register(Student, StudentAdmin)




# Enrollment Admin
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course')
    list_filter = ('course',)
    search_fields = ('student__user__first_name', 'student__user__last_name', 'course__name')

# Attendance Admin
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'date', 'status')
    list_filter = ('course', 'status', 'date')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'course__name')
    ordering = ('-date',)

# Register Models with Admin Panel
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Program, ProgramAdmin)
admin.site.register(Semester, SemesterAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Enrollment, EnrollmentAdmin)
admin.site.register(Attendance, AttendanceAdmin)

admin.site.register(CourseTeacher)
