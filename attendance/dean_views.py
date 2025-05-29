from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils import timezone
from django.template.loader import get_template, render_to_string
from xhtml2pdf import pisa
import csv
from io import StringIO
from datetime import datetime
from .models import Department, Program, Semester, Course, Student, Attendance, Dean, AdmitCardEligibility
from django.db.models import Count

@login_required
@user_passes_test(lambda u: u.role == 'dean')
def dean_dashboard(request):
    departments = Department.objects.all()
    
    # Get current admit card eligibility
    admit_card_eligibility = AdmitCardEligibility.objects.first()
    if not admit_card_eligibility:
        admit_card_eligibility = AdmitCardEligibility.objects.create(percentage=75.00)
    
    # Handle form submission
    if request.method == 'POST' and request.POST.get('action') == 'update_admit_card_eligibility':
        try:
            new_percentage = float(request.POST.get('eligibility_percentage'))
            if 0 <= new_percentage <= 100:
                admit_card_eligibility.percentage = new_percentage
                admit_card_eligibility.created_by = request.user
                admit_card_eligibility.save()
                messages.success(request, f'Admit card eligibility percentage updated to {new_percentage}%')
            else:
                messages.error(request, 'Percentage must be between 0 and 100')
        except ValueError:
            messages.error(request, 'Invalid percentage value')
    
    return render(request, 'attendance/dean_authentication_template/dean_dashboard.html', {
        'departments': departments,
        'admit_card_eligibility': admit_card_eligibility
    })

@login_required
@user_passes_test(lambda u: u.role == 'dean')
def dean_attendance_summary(request):
    try:
        # Get all departments
        departments = Department.objects.all()
        
        # Get filter parameters
        department_id = request.GET.get('department')
        program_id = request.GET.get('program')
        semester_id = request.GET.get('semester')
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        
        # Initialize context with basic data
        context = {
            'departments': departments,
            'selected_department': department_id,
            'selected_program': program_id,
            'selected_semester': semester_id,
            'from_date': from_date,
            'end_date': to_date
        }
        
        # Get programs based on selected department
        programs = []
        if department_id:
            programs = Program.objects.filter(department_id=department_id)
            context['programs'] = programs
            context['department'] = Department.objects.get(id=department_id)
        
        # Get semesters for the selected program
        semesters = []
        if program_id:
            semesters = Semester.objects.filter(program_id=program_id)
            context['semesters'] = semesters
            context['program'] = Program.objects.get(id=program_id)
        
        # Get courses and calculate attendance if all filters are present
        if all([department_id, program_id, semester_id, from_date, to_date]):
            semester = Semester.objects.get(id=semester_id)
            context['semester'] = semester
            
            # Get courses for the semester
            courses = Course.objects.filter(
                department_id=department_id,
                program_id=program_id,
                semester_id=semester_id
            )
            
            # Calculate total classes for each course
            total_classes_all = 0
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
                total_classes_all += course.total_classes
            
            context['courses'] = courses
            context['total_classes'] = total_classes_all
            
            # Get students in the program
            students = Student.objects.filter(
                department_id=department_id,
                program_id=program_id,
                semester_id=semester_id
            )
            
            # Calculate attendance for each student
            attendance_data = []
            for student in students:
                student_data = {
                    'name': student.name,
                    'courses': [],
                    'total_present': 0,
                    'total_classes': total_classes_all,
                    'overall_percentage': 0
                }
                
                total_present = 0
                
                # Calculate attendance for each course
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
                    
                    student_data['courses'].append({
                        'name': course.name,
                        'total_classes': total_classes,
                        'present_count': present_count,
                        'percentage': percentage
                    })
                    
                    student_data['total_classes'] += total_classes
                    student_data['total_present'] += present_count
                
                if student_data['total_classes'] > 0:
                    student_data['overall_percentage'] = round(
                        (student_data['total_present'] / student_data['total_classes'] * 100), 2
                    )
                
                attendance_data.append(student_data)
            
            context['students'] = attendance_data
            context['has_data'] = True
        
        return render(request, 'attendance/dean_authentication_template/attendance_summary.html', context)
        
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('dean_dashboard')

@login_required
@user_passes_test(lambda u: u.role == 'dean')
def dean_export_attendance_csv(request):
    try:
        # Get filter parameters
        department_id = request.GET.get('department')
        program_id = request.GET.get('program')
        semester_id = request.GET.get('semester')
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')

        if not all([department_id, program_id, semester_id, from_date, to_date]):
            messages.error(request, "All filter parameters are required")
            return redirect('dean_attendance_summary')

        try:
            department = Department.objects.get(id=department_id)
            program = Program.objects.get(id=program_id)
            semester = Semester.objects.get(id=semester_id)

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

            # Create CSV response
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="attendance_report_{from_date}_to_{to_date}.csv"'
            
            writer = csv.writer(response)
            
            # Write filter information
            writer.writerow(['Attendance Report'])
            writer.writerow(['Department:', department.name])
            writer.writerow(['Program:', program.name])
            writer.writerow(['Semester:', semester.name])
            writer.writerow(['Date Range:', f'{from_date} to {to_date}'])
            writer.writerow([])  # Empty row for spacing
            
            # Calculate total classes across all courses
            total_classes_all = sum(course.total_classes for course in courses)
            
            # Write header row
            header = ['Sr. No.', 'Student Name']
            for course in courses:
                header.extend([
                    f'{course.code} - Present out of {course.total_classes}',
                    f'{course.code} - %'
                ])
            header.extend([f'Total Present out of {total_classes_all}', 'Overall %'])
            writer.writerow(header)
            
            # Get students and write their data
            students = Student.objects.filter(
                department_id=department_id,
                program_id=program_id,
                semester_id=semester_id
            )
            
            for index, student in enumerate(students, 1):
                row = [index, student.name]
                
                total_present = 0
                total_classes = 0
                
                for course in courses:
                    attendance_records = Attendance.objects.filter(
                        student=student,
                        course=course,
                        date__range=[from_date, to_date]
                    )
                    
                    course_total = attendance_records.count()
                    course_present = attendance_records.filter(status='Present').count()
                    percentage = round((course_present / course_total * 100) if course_total > 0 else 0, 2)
                    
                    row.extend([f"{course_present} out of {course_total}", f'{percentage}%'])
                    total_present += course_present
                    total_classes += course_total
                
                overall_percentage = round((total_present / total_classes * 100) if total_classes > 0 else 0, 2)
                row.extend([f"{total_present} out of {total_classes}", f'{overall_percentage}%'])
                
                writer.writerow(row)
            
            return response
            
        except Exception as e:
            messages.error(request, f"Error generating CSV: {str(e)}")
            return redirect('dean_attendance_summary')

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('dean_dashboard')

@login_required
@user_passes_test(lambda u: u.role == 'dean')
def dean_export_attendance_pdf(request):
    try:
        # Get filter parameters
        department_id = request.GET.get('department')
        program_id = request.GET.get('program')
        semester_id = request.GET.get('semester')
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        
        if not all([department_id, program_id, semester_id, from_date, to_date]):
            messages.error(request, "All filter parameters are required")
            return redirect('dean_attendance_summary')
        
        try:
            department = Department.objects.get(id=department_id)
            program = Program.objects.get(id=program_id, department=department)
            semester = Semester.objects.get(id=semester_id, program=program)
            
            # Get all courses for the semester
            courses = Course.objects.filter(semester=semester)
            
            # Calculate total classes for each course
            course_total_classes = {}
            total_classes_all = 0
            for course in courses:
                attendance_records = Attendance.objects.filter(
                    course=course,
                    date__range=[from_date, to_date]
                )
                student_counts = attendance_records.values('student__name').annotate(count=Count('id'))
                total_classes = max([record['count'] for record in student_counts]) if student_counts else 0
                course_total_classes[course.id] = total_classes
                total_classes_all += total_classes
            
            # Get students
            students = Student.objects.filter(
                department_id=department_id,
                program_id=program_id,
                semester_id=semester_id
            )
            
            # Calculate attendance data for each student
            attendance_data = []
            for student in students:
                student_data = {
                    'name': student.name,
                    'courses': [],
                    'total_present': 0,
                    'total_classes': 0,
                    'overall_percentage': 0
                }
                
                total_present = 0
                total_classes = 0
                
                for course in courses:
                    attendance_records = Attendance.objects.filter(
                        student=student,
                        course=course,
                        date__range=[from_date, to_date]
                    )
                    
                    course_total = attendance_records.count()
                    course_present = attendance_records.filter(status='Present').count()
                    percentage = round((course_present / course_total * 100) if course_total > 0 else 0, 2)
                    
                    student_data['courses'].append({
                        'code': course.code,
                        'total_classes': course_total,
                        'present_count': course_present,
                        'percentage': percentage
                    })
                    
                    total_present += course_present
                    total_classes += course_total
                
                student_data['total_present'] = total_present
                student_data['total_classes'] = total_classes
                student_data['overall_percentage'] = round((total_present / total_classes * 100) if total_classes > 0 else 0, 2)
                
                attendance_data.append(student_data)
            
            # Render PDF template
            template = get_template('attendance/admin_authentication_template/attendance_pdf.html')
            html = template.render({
                'department': department,
                'program': program,
                'semester': semester,
                'courses': courses,
                'from_date': from_date,
                'to_date': to_date,
                'students': attendance_data,
                'total_classes': total_classes_all
            })
            
            # Create PDF response
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="attendance_report_{from_date}_to_{to_date}.pdf"'
            
            # Generate PDF
            pisa_status = pisa.CreatePDF(html, dest=response)
            if pisa_status.err:
                messages.error(request, 'Error generating PDF')
                return redirect('dean_attendance_summary')
            
            return response
            
        except Exception as e:
            messages.error(request, f"Error generating PDF: {str(e)}")
            return redirect('dean_attendance_summary')
            
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('dean_dashboard') 