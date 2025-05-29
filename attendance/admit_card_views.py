from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.conf import settings
import os
from datetime import datetime
from decimal import Decimal

from .models import (
    CustomUser, Student, Controller, AdmitCardRequest,
    Notification, AdmitCardEligibility, EnrollStudent, Attendance, Course
)
from .forms import AdmitCardRequestForm

@login_required
def request_admit_card(request):
    if request.user.role != 'student':
        messages.error(request, "Access denied. This page is for students only.")
        return redirect('home')
    
    try:
        student = Student.objects.get(
            enrollment_no=request.user.username
        )
        
        # Check if student already has a pending request
        pending_request = AdmitCardRequest.objects.filter(
            student=student,
            status='pending'
        ).first()
        
        if pending_request:
            messages.warning(request, "You already have a pending admit card request.")
            return redirect('student_dashboard')
        
        if request.method == 'POST':
            form = AdmitCardRequestForm(request.POST, request.FILES)
            if form.is_valid():
                admit_request = form.save(commit=False)
                admit_request.student = student
                admit_request.save()
                
                # Create notification for controllers
                controllers = CustomUser.objects.filter(role='controller')
                for controller in controllers:
                    Notification.objects.create(
                        user=controller,
                        title="New Admit Card Request",
                        message=f"Student {student.name} has requested an admit card.",
                        notification_type='request'
                    )
                
                messages.success(request, "Your admit card request has been submitted successfully.")
                return redirect('student_dashboard')
        else:
            form = AdmitCardRequestForm()
        
        return render(request, 'attendance/student_authentication_template/request_admit_card.html', {
            'form': form,
            'student': student
        })
        
    except Student.DoesNotExist:
        messages.error(request, "Student record not found.")
        return redirect('student_dashboard')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('student_dashboard')

@login_required
def view_admit_card_requests(request):
    if request.user.role != 'dean':
        messages.error(request, "Access denied. This page is for deans only.")
        return redirect('home')
    
    try:
        # No need to get controller, just show all requests
        if request.method == 'POST':
            request_id = request.POST.get('request_id')
            action = request.POST.get('action')
            
            try:
                admit_request = AdmitCardRequest.objects.get(id=request_id)
                
                if action == 'approve':
                    relaxation_percentage = request.POST.get('relaxation_percentage')
                    review_notes = request.POST.get('review_notes', '')
                    admit_request.status = 'approved'
                    admit_request.relaxation_percentage = relaxation_percentage
                    admit_request.review_notes = review_notes
                    admit_request.reviewed_by = request.user
                    admit_request.save()
                    Notification.objects.create(
                        user=admit_request.student.user,
                        title="Admit Card Request Approved",
                        message=f"Your admit card request has been approved with {relaxation_percentage}% attendance relaxation.",
                        notification_type='request'
                    )
                    messages.success(request, "Admit card request approved successfully.")
                elif action == 'reject':
                    review_notes = request.POST.get('review_notes')
                    admit_request.status = 'rejected'
                    admit_request.review_notes = review_notes
                    admit_request.reviewed_by = request.user
                    admit_request.save()
                    Notification.objects.create(
                        user=admit_request.student.user,
                        title="Admit Card Request Rejected",
                        message=f"Your admit card request has been rejected. Reason: {review_notes}",
                        notification_type='request'
                    )
                    messages.success(request, "Admit card request rejected successfully.")
            except AdmitCardRequest.DoesNotExist:
                messages.error(request, "Admit card request not found.")
        requests = AdmitCardRequest.objects.all().select_related('student', 'student__department').order_by('-created_at')
        return render(request, 'attendance/dean_authentication_template/admit_card_requests.html', {
            'requests': requests
        })
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('home')

@login_required
def approve_admit_card_request(request, request_id):
    if request.user.role != 'dean':
        return redirect('login')
    try:
        admit_request = AdmitCardRequest.objects.get(id=request_id)
        if request.method == 'POST':
            relaxation_percentage = request.POST.get('relaxation_percentage')
            review_notes = request.POST.get('review_notes')
            if relaxation_percentage:
                current_eligibility = AdmitCardEligibility.objects.first()
                if not current_eligibility:
                    current_eligibility = AdmitCardEligibility.objects.create(percentage=75.00)
                enrollment = EnrollStudent.objects.filter(
                    user__username=admit_request.student.enrollment_no
                ).first()
                if not enrollment:
                    messages.error(request, "Student is not enrolled in any program.")
                    return redirect('view_admit_card_requests')
                attendance_records = Attendance.objects.filter(
                    student__enrollment_no=admit_request.student.enrollment_no,
                    course__semester=enrollment.semester
                )
                total_classes = attendance_records.count()
                present_count = attendance_records.filter(status='Present').count()
                overall_attendance = (present_count / total_classes * 100) if total_classes > 0 else 0
                current_eligibility_percentage = Decimal(str(current_eligibility.percentage))
                relaxation_percentage_decimal = Decimal(str(relaxation_percentage))
                new_required_percentage = current_eligibility_percentage - relaxation_percentage_decimal
                admit_request.relaxation_percentage = float(relaxation_percentage)
                admit_request.review_notes = review_notes
                admit_request.status = 'approved'
                admit_request.save()
                student_user = CustomUser.objects.get(username=admit_request.student.enrollment_no)
                notification_message = (
                    f"Your admit card request has been approved!\n\n"
                    f"Current Attendance Criteria: {current_eligibility_percentage}%\n"
                    f"Your Current Attendance: {overall_attendance:.2f}%\n"
                    f"Relaxation Granted: {relaxation_percentage}%\n"
                    f"New Required Attendance: {new_required_percentage:.2f}%\n\n"
                    f"Since your attendance ({overall_attendance:.2f}%) is now above the adjusted requirement "
                    f"({new_required_percentage:.2f}%), you can now download your admit card.\n\n"
                    f"Go to your dashboard and click on 'Download Admit Card' to get your admit card."
                )
                Notification.objects.create(
                    user=student_user,
                    title='Admit Card Request Approved',
                    message=notification_message,
                    notification_type='admit_card_request'
                )
                messages.success(request, 'Admit card request approved successfully.')
        context = {
            'admit_request': admit_request,
            'student': admit_request.student
        }
        return render(request, 'attendance/dean_authentication_template/approve_admit_card_request.html', context)
    except AdmitCardRequest.DoesNotExist:
        messages.error(request, 'Admit card request not found.')
        return redirect('view_admit_card_requests')
    except CustomUser.DoesNotExist:
        messages.error(request, 'Student user record not found.')
        return redirect('view_admit_card_requests')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('view_admit_card_requests')

@login_required
def download_admit_card(request):
    try:
        # Check if user is a student
        if not hasattr(request.user, 'student'):
            messages.error(request, "Only students can download admit cards.")
            return redirect('student_dashboard')

        # Get student's enrollment
        enrollment = EnrollStudent.objects.filter(user=request.user).first()
        if not enrollment:
            messages.error(request, "You are not enrolled in any program.")
            return redirect('student_dashboard')

        # Get student's attendance records
        attendance_records = Attendance.objects.filter(
            student__enrollment_no=request.user.username,
            course__semester=enrollment.semester
        )

        if not attendance_records.exists():
            messages.error(request, "No attendance records found.")
            return redirect('student_dashboard')

        # Calculate overall attendance
        total_classes = attendance_records.count()
        present_count = attendance_records.filter(status='Present').count()
        overall_attendance = (present_count / total_classes * 100) if total_classes > 0 else 0

        # Get current eligibility criteria
        eligibility = AdmitCardEligibility.objects.first()
        if not eligibility:
            eligibility = AdmitCardEligibility.objects.create(percentage=75.00)

        required_percentage = eligibility.percentage

        # Check for any approved admit card request
        approved_request = AdmitCardRequest.objects.filter(
            student__enrollment_no=request.user.username,
            status='approved',
            created_at__gt=eligibility.last_modified
        ).first()

        if approved_request:
            required_percentage -= approved_request.relaxation_percentage

        # Check if student meets the criteria
        if overall_attendance < required_percentage:
            error_message = f"""
            You are not eligible to download the admit card.
            
            Your current attendance: {overall_attendance:.2f}%
            Required attendance: {required_percentage:.2f}%
            
            Please request a relaxation from the controller if you have valid reasons for low attendance.
            """
            messages.error(request, error_message)
            
            # Create a notification for the student
            Notification.objects.create(
                user=request.user,
                title="Admit Card Download Failed",
                message=error_message,
                notification_type='admit_card'
            )
            
            return redirect('student_dashboard')

        # Get student details
        student = Student.objects.get(enrollment_no=request.user.username)
        
        # Get all courses for the semester
        courses = Course.objects.filter(semester=enrollment.semester)
        
        # Calculate attendance for each course
        course_attendance = []
        for course in courses:
            course_records = attendance_records.filter(course=course)
            course_total = course_records.count()
            course_present = course_records.filter(status='Present').count()
            course_percentage = (course_present / course_total * 100) if course_total > 0 else 0
            
            course_attendance.append({
                'code': course.code,
                'name': course.name,
                'attendance': f"{course_percentage:.2f}%"
            })

        # Create PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="admit_card_{student.enrollment_no}.pdf"'
        
        # Generate PDF content
        p = canvas.Canvas(response)
        
        # Add university logo
        try:
            p.drawImage('static/images/amu_logo.png', 50, 750, width=100, height=100)
        except:
            pass  # Continue if logo not found
        
        # Add header
        p.setFont("Helvetica-Bold", 16)
        p.drawString(200, 800, "ALIGARH MUSLIM UNIVERSITY")
        p.setFont("Helvetica-Bold", 14)
        p.drawString(200, 780, "Admit Card")
        
        # Add student details
        p.setFont("Helvetica", 12)
        y = 700
        details = [
            ("Enrollment No:", student.enrollment_no),
            ("Name:", student.name),
            ("Program:", enrollment.program.name),
            ("Semester:", enrollment.semester.name),
            ("Overall Attendance:", f"{overall_attendance:.2f}%"),
            ("Required Attendance:", f"{required_percentage:.2f}%")
        ]
        
        for label, value in details:
            p.drawString(50, y, f"{label} {value}")
            y -= 20
        
        # Add course-wise attendance
        y -= 20
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, "Course-wise Attendance:")
        y -= 20
        
        p.setFont("Helvetica", 10)
        for course in course_attendance:
            p.drawString(50, y, f"{course['code']} - {course['name']}: {course['attendance']}")
            y -= 15
        
        # Add footer
        p.setFont("Helvetica-Oblique", 8)
        p.drawString(50, 50, "This is a computer-generated document. No signature required.")
        
        p.showPage()
        p.save()
        
        return response
        
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('student_dashboard') 