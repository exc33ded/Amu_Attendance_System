from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.db.models import Count
import random
import string
import csv
from datetime import datetime
from django.views.decorators.http import require_http_methods
from django.template.loader import get_template
from django.utils import timezone
from xhtml2pdf import pisa
from django.template.loader import render_to_string

from .models import CustomUser, Department, Teacher, Controller, Notification, Program, Semester, Course, Attendance, Student, EnrollStudent, AdmitCardEligibility, AttendanceChangeRequest, AdmitCardRequest

def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

@login_required
@user_passes_test(is_admin)
def manage_controllers(request):
    departments = Department.objects.all()
    controllers = Controller.objects.all().order_by('department__name')
    
    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')
        department_id = request.POST.get('department_id')
        
        try:
            teacher_user = CustomUser.objects.get(id=teacher_id, role='faculty')
            department = Department.objects.get(id=department_id)
            teacher = Teacher.objects.get(user=teacher_user)
            if teacher.department != department:
                messages.error(request, "Selected teacher does not belong to the chosen department.")
                return redirect('manage_controllers')
            if Controller.objects.filter(department=department, is_active=True).exists():
                messages.error(request, f"Department {department.name} already has a controller.")
                return redirect('manage_controllers')
            original_email = teacher_user.email
            controller_email = original_email.replace('@', '_controller@')
            controller_username = f"{teacher_user.username}_controller"
            temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            controller_user = CustomUser.objects.create_user(
                username=controller_username,
                email=controller_email,
                password=temp_password,
                first_name=teacher_user.first_name,
                last_name=teacher_user.last_name,
                role='controller'
            )
            controller = Controller.objects.create(
                user=controller_user,
                department=department,
                teacher=teacher,
                is_active=True
            )
            notification_message = f"""
Congratulations! You have been appointed as the Controller of Aligarh Muslim University.\n\nYour Controller Login Credentials:\nUsername: {controller_username}\nPassword: {temp_password}\n\nPlease log in to the unified login page with these credentials.\nFor security reasons, you will be required to change your password upon first login.\n\nNote: This is a separate account for your controller role. You can continue to use your faculty account ({teacher_user.username}) for faculty-related activities.
            """
            Notification.objects.create(
                user=teacher_user,
                title=f"Controller Appointment - {department.name}",
                message=notification_message,
                notification_type='appointment'
            )
            messages.success(request, f"Controller role has been assigned to {teacher_user.get_full_name()}")
            return redirect('manage_controllers')
        except Exception as e:
            messages.error(request, f"Error assigning controller: {str(e)}")
    return render(request, 'attendance/admin_authentication_template/manage_controllers.html', {
        'departments': departments,
        'controllers': controllers
    })

@login_required
@user_passes_test(is_admin)
def remove_controller(request, controller_id):
    try:
        controller = Controller.objects.select_related('user', 'department').get(id=controller_id)
        department_name = controller.department.name
        controller_user = controller.user
        teacher_user = CustomUser.objects.get(
            username=controller_user.username.replace('_controller', ''),
            role='faculty'
        )
        notification_message = f"""
Your controller role for Aligarh Muslim Universityhas been removed.\nYour controller account ({controller_user.username}) has been deactivated.\n\nYou can continue to use your faculty account ({teacher_user.username}) for faculty-related activities.
        """
        Notification.objects.create(
            user=teacher_user,
            title=f"Controller Role Removed - {department_name}",
            message=notification_message,
            notification_type='removal'
        )
        try:
            send_mail(
                f"Controller Role Removed - {department_name}",
                notification_message,
                settings.DEFAULT_FROM_EMAIL,
                [teacher_user.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error sending email: {str(e)}")
        controller_user.delete()
        messages.success(request, f"Controller role has been removed from {teacher_user.get_full_name()}")
    except Controller.DoesNotExist:
        messages.error(request, "Controller record not found.")
    except Exception as e:
        messages.error(request, f"Error removing controller: {str(e)}")
    return redirect('manage_controllers')

@login_required
def controller_dashboard(request):
    if not hasattr(request.user, 'controller'):
        messages.error(request, "You are not authorized to access this page.")
        return redirect('home')

    # Get department statistics
    departments = Department.objects.all()
    department_stats = []
    for dept in departments:
        stats = {
            'department': dept,
            'teachers_count': Teacher.objects.filter(department=dept).count(),
            'students_count': Student.objects.filter(department=dept).count(),
            'courses_count': Course.objects.filter(department=dept).count(),
            'programs_count': Program.objects.filter(department=dept).count()
        }
        department_stats.append(stats)

    # Get total counts
    total_teachers = Teacher.objects.count()
    total_students = Student.objects.count()
    total_courses = Course.objects.count()

    # Get notifications for the controller
    notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by('-created_at')[:5]
    
    unread_notifications_count = notifications.count()

    context = {
        'department_stats': department_stats,
        'total_teachers': total_teachers,
        'total_students': total_students,
        'total_courses': total_courses,
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count
    }
    return render(request, 'attendance/controller_authentication_template/controller_dashboard.html', context)

@login_required
def controller_export_attendance_csv(request):
    if not request.user.role == 'controller':
        return redirect('login')
    
    # Get filter parameters
    department_id = request.GET.get('department')
    program_id = request.GET.get('program')
    semester_id = request.GET.get('semester')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    
    if not all([department_id, program_id, semester_id, from_date, to_date]):
        messages.error(request, 'Missing required parameters')
        return redirect('controller_attendance_summary')
    
    try:
        department = Department.objects.get(id=department_id)
        program = Program.objects.get(id=program_id)
        semester = Semester.objects.get(id=semester_id)
        
        # Get all courses for the semester
        courses = Course.objects.filter(
            semester=semester,
            program=program,
            department=department
        )
        
        # Get all enrolled students for the program and semester
        enroll_students = EnrollStudent.objects.filter(
            program=program,
            semester=semester
        ).select_related('user')
        
        # Calculate total classes for each course
        for course in courses:
            # Get all attendance records for this course
            attendance_records = Attendance.objects.filter(
                course=course,
                date__range=[from_date, to_date]
            )
            
            # Count how many times each student name appears
            student_counts = attendance_records.values('student__name').annotate(count=Count('id'))
            
            # Get the maximum count (this will be the total classes for this course)
            course.total_classes = max([record['count'] for record in student_counts]) if student_counts else 0
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="attendance_summary_{department.name}_{program.name}_{semester.name}.csv"'
        
        writer = csv.writer(response)
        
        # Write filter information
        writer.writerow(['Attendance Summary Report'])
        writer.writerow(['Department:', department.name])
        writer.writerow(['Program:', program.name])
        writer.writerow(['Semester:', semester.name])
        writer.writerow(['Date Range:', f'{from_date} to {to_date}'])
        writer.writerow([])  # Empty row for spacing
        
        # Write header with total classes
        header = ['Student Name']
        for course in courses:
            header.extend([f'{course.code} (Present)', f'{course.code} (%)'])
        header.extend(['Total Present', 'Overall %'])
        writer.writerow(header)
        
        # Write total classes row
        total_classes_row = ['Total Classes:']
        for course in courses:
            total_classes_row.extend([course.total_classes, ''])
        total_classes_row.extend(['', ''])
        writer.writerow(total_classes_row)
        
        # Write data rows
        students = []
        for enroll_student in enroll_students:
            try:
                # Get the Student model instance using the enrollment number
                student = Student.objects.get(
                    enrollment_no=enroll_student.user.username,
                    program=program,
                    semester=semester
                )
                
                row = [student.name]
                total_present = 0
                total_classes_count = 0
                
                for course in courses:
                    # Get attendance records for this student and course
                    attendance_records = Attendance.objects.filter(
                        student=student,
                        course=course,
                        date__range=[from_date, to_date]
                    )
                    
                    # Count total classes and present count for this student and course
                    total_classes = attendance_records.count()
                    present_count = attendance_records.filter(status='Present').count()
                    percentage = round((present_count / total_classes * 100) if total_classes > 0 else 0, 2)
                    
                    row.extend([present_count, f'{percentage}%'])
                    
                    total_present += present_count
                    total_classes_count += total_classes
                
                overall_percentage = round((total_present / total_classes_count * 100) if total_classes_count > 0 else 0, 2)
                row.extend([total_present, f'{overall_percentage}%'])
                
                writer.writerow(row)
                students.append(student)
            except Student.DoesNotExist:
                continue
        
        # Write summary statistics
        writer.writerow([])  # Empty row for spacing
        writer.writerow(['Summary Statistics'])
        writer.writerow(['Total Students:', len(students)])
        writer.writerow(['Total Courses:', len(courses)])
        writer.writerow(['Date Range:', f'{from_date} to {to_date}'])
        
        return response
        
    except (Department.DoesNotExist, Program.DoesNotExist, Semester.DoesNotExist) as e:
        messages.error(request, str(e))
        return redirect('controller_attendance_summary')

@login_required
def controller_export_attendance_pdf(request):
    if not request.user.role == 'controller':
        return redirect('login')
    
    # Get filter parameters
    department_id = request.GET.get('department')
    program_id = request.GET.get('program')
    semester_id = request.GET.get('semester')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    
    if not all([department_id, program_id, semester_id, from_date, to_date]):
        messages.error(request, 'Missing required parameters')
        return redirect('controller_attendance_summary')
    
    try:
        department = Department.objects.get(id=department_id)
        program = Program.objects.get(id=program_id)
        semester = Semester.objects.get(id=semester_id)
        
        # Get all courses for the semester
        courses = Course.objects.filter(
            semester=semester,
            program=program,
            department=department
        )
        
        # Get all enrolled students for the program and semester
        enroll_students = EnrollStudent.objects.filter(
            program=program,
            semester=semester
        ).select_related('user')
        
        # Calculate total classes for each course
        for course in courses:
            # Get all attendance records for this course
            attendance_records = Attendance.objects.filter(
                course=course,
                date__range=[from_date, to_date]
            )
            
            # Count how many times each student name appears
            student_counts = attendance_records.values('student__name').annotate(count=Count('id'))
            
            # Get the maximum count (this will be the total classes for this course)
            course.total_classes = max([record['count'] for record in student_counts]) if student_counts else 0
        
        # Get attendance records for each student
        student_attendance = []
        for enroll_student in enroll_students:
            try:
                # Get the Student model instance using the enrollment number
                student = Student.objects.get(
                    enrollment_no=enroll_student.user.username,
                    program=program,
                    semester=semester
                )
                
                attendance_data = {
                    'name': student.name,
                    'courses': [],
                    'total_present': 0,
                    'total_classes': 0
                }
                
                for course in courses:
                    # Get attendance records for this student and course
                    attendance_records = Attendance.objects.filter(
                        student=student,
                        course=course,
                        date__range=[from_date, to_date]
                    )
                    
                    # Count total classes and present count for this student and course
                    total_classes = attendance_records.count()
                    present_count = attendance_records.filter(status='Present').count()
                    percentage = round((present_count / total_classes * 100) if total_classes > 0 else 0, 2)
                    
                    attendance_data['courses'].append({
                        'present_count': present_count,
                        'percentage': percentage
                    })
                    
                    attendance_data['total_present'] += present_count
                    attendance_data['total_classes'] += total_classes
                
                if attendance_data['total_classes'] > 0:
                    attendance_data['overall_percentage'] = round(
                        (attendance_data['total_present'] / attendance_data['total_classes'] * 100), 2
                    )
                else:
                    attendance_data['overall_percentage'] = 0
                
                student_attendance.append(attendance_data)
            except Student.DoesNotExist:
                continue
        
        # Render PDF template
        html_string = render_to_string('attendance/controller_authentication_template/attendance_pdf.html', {
            'department': department,
            'program': program,
            'semester': semester,
            'courses': courses,
            'students': student_attendance,
            'from_date': from_date,
            'to_date': to_date,
            'total_classes': sum(course.total_classes for course in courses),
            'generated_at': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            'controller_name': request.user.get_full_name() or request.user.username
        })
        
        # Create PDF response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="attendance_summary_{department.name}_{program.name}_{semester.name}.pdf"'
        
        # Generate PDF
        pisa_status = pisa.CreatePDF(html_string, dest=response)
        
        if pisa_status.err:
            return HttpResponse('Error generating PDF')
        
        return response
        
    except (Department.DoesNotExist, Program.DoesNotExist, Semester.DoesNotExist) as e:
        messages.error(request, str(e))
        return redirect('controller_attendance_summary')

@require_http_methods(["GET"])
def get_programs_by_department(request, department_id=None):
    try:
        if department_id is None:
            department_id = request.GET.get('department')
        
        if not department_id:
            return JsonResponse({'error': 'Department ID is required'}, status=400)
        
        programs = Program.objects.filter(department_id=department_id)
        data = [{'id': program.id, 'name': program.name} for program in programs]
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def get_semesters_by_program(request, program_id=None):
    try:
        if program_id is None:
            program_id = request.GET.get('program')
        
        if not program_id:
            return JsonResponse({'error': 'Program ID is required'}, status=400)
        
        semesters = Semester.objects.filter(program_id=program_id)
        data = [{'id': semester.id, 'name': semester.name} for semester in semesters]
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def get_courses_by_semester(request):
    try:
        department_id = request.GET.get('department')
        program_id = request.GET.get('program')
        semester_id = request.GET.get('semester')
        
        if not all([department_id, program_id, semester_id]):
            return JsonResponse({'error': 'All parameters are required'}, status=400)
        
        courses = Course.objects.filter(
            department_id=department_id,
            program_id=program_id,
            semester_id=semester_id
        )
        data = [{'id': course.id, 'name': f"{course.code} - {course.name}"} for course in courses]
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def controller_attendance_summary(request):
    if not request.user.role == 'controller':
        return redirect('login')
    
    departments = Department.objects.all()
    programs = Program.objects.none()
    semesters = Semester.objects.none()
    courses = Course.objects.none()
    
    # Get filter parameters
    department_id = request.GET.get('department')
    program_id = request.GET.get('program')
    semester_id = request.GET.get('semester')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    
    # Get programs based on selected department
    if department_id:
        programs = Program.objects.filter(department_id=department_id)
    
    # Get semesters based on selected program
    if program_id:
        semesters = Semester.objects.filter(program_id=program_id)
    
    # Get courses based on selected semester
    if semester_id:
        courses = Course.objects.filter(semester_id=semester_id)
    
    # Initialize context
    context = {
        'departments': departments,
        'programs': programs,
        'semesters': semesters,
        'courses': courses,
        'selected_department': department_id,
        'selected_program': program_id,
        'selected_semester': semester_id,
        'from_date': from_date,
        'to_date': to_date
    }
    
    # If filters are applied
    if department_id and program_id and semester_id and from_date and to_date:
        try:
            department = Department.objects.get(id=department_id)
            program = Program.objects.get(id=program_id, department=department)
            semester = Semester.objects.get(id=semester_id, program=program)
            
            # Get all courses for the semester
            courses = Course.objects.filter(semester=semester)
            
            # Calculate total classes for each course
            for course in courses:
                # Get all attendance records for this course
                attendance_records = Attendance.objects.filter(
                    course=course,
                    date__range=[from_date, to_date]
                )
                
                # Count how many times each student name appears
                student_counts = attendance_records.values('student__name').annotate(count=Count('id'))
                
                # Get the maximum count (this will be the total classes for this course)
                course.total_classes = max([record['count'] for record in student_counts]) if student_counts else 0
            
            # Get all enrolled students for the program and semester
            enroll_students = EnrollStudent.objects.filter(
                program=program,
                semester=semester
            ).select_related('user')
            
            students = []
            for enroll_student in enroll_students:
                try:
                    # Get the Student model instance using the enrollment number
                    student = Student.objects.get(
                        enrollment_no=enroll_student.user.username,
                        program=program,
                        semester=semester
                    )
                    
                    student_info = {
                        'name': student.name,
                        'courses': [],
                        'total_classes': 0,
                        'total_present': 0,
                        'overall_percentage': 0
                    }
                    
                    for course in courses:
                        # Get attendance records for this student and course
                        attendance_records = Attendance.objects.filter(
                            student=student,
                            course=course,
                            date__range=[from_date, to_date]
                        )
                        
                        # Count total classes and present count for this student and course
                        total_classes = attendance_records.count()
                        present_count = attendance_records.filter(status='Present').count()
                        percentage = round((present_count / total_classes * 100) if total_classes > 0 else 0, 2)
                        
                        student_info['courses'].append({
                            'name': course.name,
                            'total_classes': total_classes,
                            'present_count': present_count,
                            'percentage': percentage
                        })
                        
                        student_info['total_classes'] += total_classes
                        student_info['total_present'] += present_count
                    
                    if student_info['total_classes'] > 0:
                        student_info['overall_percentage'] = round(
                            (student_info['total_present'] / student_info['total_classes'] * 100), 2
                        )
                    
                    students.append(student_info)
                except Student.DoesNotExist:
                    # Skip students that don't have a corresponding Student record
                    continue
            
            # Calculate total classes across all courses
            total_classes = sum(course.total_classes for course in courses)
            
            context.update({
                'department': department,
                'program': program,
                'semester': semester,
                'courses': courses,
                'students': students,
                'total_classes': total_classes,
                'has_data': True  # Add flag to indicate data is available
            })
            
        except (Program.DoesNotExist, Semester.DoesNotExist) as e:
            messages.error(request, str(e))
    
    return render(request, 'attendance/controller_authentication_template/attendance_summary.html', context)

@login_required
def controller_attendance_report(request):
    if not request.user.role == 'controller':
        return redirect('login')
    
    # Get filter parameters
    department_id = request.GET.get('department')
    program_id = request.GET.get('program')
    semester_id = request.GET.get('semester')
    start_date = request.GET.get('from_date')
    end_date = request.GET.get('to_date')
    
    if not all([department_id, program_id, semester_id, start_date, end_date]):
        messages.error(request, 'Missing required parameters')
        return redirect('controller_attendance_summary')
    
    try:
        department = Department.objects.get(id=department_id)
        program = Program.objects.get(id=program_id, department=department)
        semester = Semester.objects.get(id=semester_id, program=program)
        
        # Get all courses for the semester
        courses = Course.objects.filter(
            semester=semester,
            program=program,
            department=department
        )
        
        # Get all students in the program
        students = Student.objects.filter(program=program)
        
        # Calculate attendance for each student
        student_data = []
        total_classes = 0
        
        for student in students:
            student_courses = {}
            student_total_present = 0
            student_total_classes = 0
            
            for course in courses:
                # Get attendance records for this course
                attendance_records = Attendance.objects.filter(
                    student=student,
                    course=course,
                    date__range=[start_date, end_date]
                ).order_by('date')
                
                # Calculate total classes and present count
                total_course_classes = attendance_records.count()
                present_count = attendance_records.filter(status='present').count()
                
                # Calculate percentage
                percentage = (present_count / total_course_classes * 100) if total_course_classes > 0 else 0
                
                # Store course data
                student_courses[course.id] = {
                    'present': present_count,
                    'total': total_course_classes,
                    'percentage': percentage,
                    'records': attendance_records
                }
                
                # Update totals
                student_total_present += present_count
                student_total_classes += total_course_classes
            
            # Calculate overall percentage
            overall_percentage = (student_total_present / student_total_classes * 100) if student_total_classes > 0 else 0
            
            student_data.append({
                'student': student,
                'courses': student_courses,
                'total_present': student_total_present,
                'total_classes': student_total_classes,
                'overall_percentage': overall_percentage
            })
            
            # Update total classes (use the maximum number of classes across all students)
            total_classes = max(total_classes, student_total_classes)
        
        context = {
            'department': department,
            'program': program,
            'semester': semester,
            'courses': courses,
            'start_date': start_date,
            'end_date': end_date,
            'students': student_data,
            'total_classes': total_classes
        }
        
        return render(request, 'attendance/controller_authentication_template/attendance_report.html', context)
        
    except (Department.DoesNotExist, Program.DoesNotExist, Semester.DoesNotExist) as e:
        messages.error(request, str(e))
        return redirect('controller_attendance_summary') 