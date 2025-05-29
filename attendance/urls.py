from django.urls import path
from . import views
from . import controller_views
from . import admit_card_views
from .controller_views import (
    manage_controllers,
    remove_controller,
    controller_dashboard,
    controller_export_attendance_csv,
    controller_export_attendance_pdf,
    controller_attendance_summary,
    get_programs_by_department,
    get_semesters_by_program,
    get_courses_by_semester
)
from . import dean_views

urlpatterns = [
    # Home & Authentication
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout_view, name='logout'),

    # Admin Authentication & Dashboard
    path('admin-login/', views.admin_login, name='admin_login'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('register/admin/', views.register_admin, name='register_admin'),

    # Department Management
    path('dashboard/admin/departments/', views.manage_department, name='manage_department'),
    path('dashboard/admin/departments/add/', views.add_department, name='add_department'),
    path('dashboard/admin/departments/edit/<int:dept_id>/', views.edit_department, name='edit_department'),
    path('dashboard/admin/departments/delete/<int:dept_id>/', views.delete_department, name='delete_department'),

    # Program Management
    path('dashboard/admin/programs/', views.manage_programs, name='manage_programs'),
    path('dashboard/admin/programs/add/', views.add_program, name='add_program'),
    path('dashboard/admin/programs/edit/<int:program_id>/', views.edit_program, name='edit_program'),
    path('dashboard/admin/programs/delete/<int:program_id>/', views.delete_program, name='delete_program'),

    # Semester Management
    path('dashboard/admin/semesters/', views.manage_semesters, name='manage_semesters'),
    path('dashboard/admin/semesters/edit/<int:semester_id>/', views.edit_semester, name='edit_semester'),
    path('dashboard/admin/semesters/delete/<int:semester_id>/', views.delete_semester, name='delete_semester'),

    # Course Management
    path('dashboard/admin/courses/', views.manage_courses, name='manage_courses'),
    path('dashboard/admin/courses/add/', views.add_course, name='add_course'),
    path('dashboard/admin/courses/edit/<int:course_id>/', views.edit_course, name='edit_course'),
    path('dashboard/admin/courses/delete/<int:course_id>/', views.delete_course, name='delete_course'),
    path('get-programs/', views.get_programs, name='get_programs'),
    path('get-semesters/', views.get_semesters, name='get_semesters'),

    # Teacher Management
    path('dashboard/admin/teachers/', views.manage_teachers, name='manage_teachers'),
    path('dashboard/admin/teachers/edit/<int:teacher_id>/', views.edit_teacher, name='edit_teacher'),
    path('dashboard/admin/teachers/delete/<int:teacher_id>/', views.delete_teacher, name='delete_teacher'),

    # Student Management
    path('dashboard/admin/students/', views.manage_students, name='manage_students'),
    path('dashboard/admin/students/edit/<int:student_id>/', views.edit_student, name='edit_student'),
    path('dashboard/admin/students/delete/<int:student_id>/', views.delete_student, name='delete_student'),

    # Teacher Assignment URLs
    path('dashboard/admin/assign-teacher/', views.assign_teacher, name='assign_teacher'),
    path('dashboard/admin/edit-course-assignment/<int:assignment_id>/', views.edit_course_assignment, name='edit_course_assignment'),
    path('dashboard/admin/remove-course-assignment/<int:assignment_id>/', views.remove_course_assignment, name='remove_course_assignment'),
    
    # AJAX endpoints for teacher assignment
    path('ajax/get-teachers-by-department/', views.get_teachers_by_department, name='get_teachers_by_department'),
    path('ajax/get-teachers-by-department/<int:department_id>/', views.get_teachers_by_department, name='get_teachers_by_department_with_id'),
    path('ajax/get-programs-by-department/', views.get_programs_by_department, name='get_programs_by_department'),
    path('ajax/get-semesters-by-program/', views.get_semesters_by_program, name='get_semesters_by_program'),
    path('ajax/get-courses/', views.get_courses, name='get_courses'),

    # Teacher Authentication & Dashboard
    path('register/teacher/', views.register_teacher, name='register_teacher'),
    path('teacher-login/', views.teacher_login, name='teacher_login'),
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/teacher/course/<int:course_id>/students/', views.view_course_students, name='view_course_students'),
    path('dashboard/teacher/mark-attendance/<int:course_id>/', views.mark_attendance, name='mark_attendance'),
    path('dashboard/teacher/course/<int:course_id>/export-csv/', views.export_attendance_csv, name='export_attendance_csv'),
    path('dashboard/teacher/course/<int:course_id>/export-pdf/', views.export_attendance_pdf, name='export_attendance_pdf'),
    path('dashboard/teacher/course/<int:course_id>/view-attendance/', views.view_attendance, name='view_attendance'),
    path('dashboard/teacher/approve-attendance-change/<int:request_id>/', views.approve_attendance_change, name='approve_attendance_change'),
    path('dashboard/teacher/reject-attendance-change/<int:request_id>/', views.reject_attendance_change, name='reject_attendance_change'),

    # Student Authentication & Dashboard
    path('register/student/', views.student_register, name='student_register'),
    path('student-login/', views.student_login, name='student_login'),
    path('student-logout/', views.student_logout, name='student_logout'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/download-enrollment-card/', views.download_enrollment_card, name='download_enrollment_card'),
    path('student/download-admit-card/', admit_card_views.download_admit_card, name='download_admit_card'),
    path('student/view-attendance/', views.student_view_attendance, name='student_view_attendance'),
    path('student/export-attendance-csv/', views.export_student_attendance_csv, name='export_student_attendance_csv'),
    path('student/export-attendance-pdf/', views.export_student_attendance_pdf, name='export_student_attendance_pdf'),
    path('student/request-attendance-change/', views.student_request_attendance_change, name='student_request_attendance_change'),
    path('student/submit-attendance-change-request/', views.submit_attendance_change_request, name='submit_attendance_change_request'),

    # Reports & Exports
    path('dashboard/admin/view-attendance/', views.view_attendance, name='view_attendance'),
    path('dashboard/admin/export-attendance/', views.export_attendance, name='export_attendance'),
    path('dashboard/admin/generate-reports/', views.generate_reports, name='generate_reports'),

    # Attendance Summary URLs
    path('summary/', views.attendance_summary, name='attendance_summary'),
    path('attendance/report/', views.attendance_report, name='attendance_report'),
    path('export-attendance-csv/', views.admin_export_attendance_csv, name='admin_export_attendance_csv'),
    path('export-attendance-pdf/', views.admin_export_attendance_pdf, name='admin_export_attendance_pdf'),

    # Chairperson URLs
    path('chairperson/register/', views.register_chairperson, name='register_chairperson'),
    path('chairperson/login/', views.chairperson_login, name='chairperson_login'),
    path('chairperson/dashboard/', views.chairperson_dashboard, name='chairperson_dashboard'),
    path('chairperson/change-password/', views.chairperson_change_password, name='chairperson_change_password'),
    path('chairperson/manage-teachers/', views.chairperson_manage_teachers, name='chairperson_manage_teachers'),
    path('chairperson/edit-teacher/<int:teacher_id>/', views.chairperson_edit_teacher, name='chairperson_edit_teacher'),
    path('chairperson/delete-teacher/<int:teacher_id>/', views.chairperson_delete_teacher, name='chairperson_delete_teacher'),
    path('chairperson/manage-courses/', views.chairperson_manage_courses, name='chairperson_manage_courses'),
    path('chairperson/add-course/', views.chairperson_add_course, name='chairperson_add_course'),
    path('chairperson/edit-course/<int:course_id>/', views.chairperson_edit_course, name='chairperson_edit_course'),
    path('chairperson/delete-course/<int:course_id>/', views.chairperson_delete_course, name='chairperson_delete_course'),
    path('chairperson/manage-students/', views.chairperson_manage_students, name='chairperson_manage_students'),
    path('chairperson/assign-teacher/', views.chairperson_assign_teacher, name='chairperson_assign_teacher'),
    path('chairperson/edit-course-assignment/<int:assignment_id>/', views.chairperson_edit_course_assignment, name='chairperson_edit_course_assignment'),
    path('chairperson/remove-course-assignment/<int:assignment_id>/', views.chairperson_remove_course_assignment, name='chairperson_remove_course_assignment'),
    path('chairperson/manage-programs/', views.chairperson_manage_programs, name='chairperson_manage_programs'),
    path('chairperson/add-program/', views.chairperson_add_program, name='chairperson_add_program'),
    path('chairperson/edit-program/<int:program_id>/', views.chairperson_edit_program, name='chairperson_edit_program'),
    path('chairperson/delete-program/<int:program_id>/', views.chairperson_delete_program, name='chairperson_delete_program'),
    path('chairperson/manage-semesters/', views.chairperson_manage_semesters, name='chairperson_manage_semesters'),
    path('chairperson/attendance/summary/', views.chairperson_attendance_summary, name='chairperson_attendance_summary'),
    path('chairperson/attendance/export/csv/', views.chairperson_export_attendance_csv, name='chairperson_export_attendance_csv'),
    path('chairperson/attendance/export/pdf/', views.chairperson_export_attendance_pdf, name='chairperson_export_attendance_pdf'),
    path('chairperson/get-courses-by-semester/', views.get_courses_by_semester, name='get_courses_by_semester'),
    path('chairperson/attendance-change-requests/', views.attendance_change_requests_chairperson, name='attendance_change_requests_chairperson'),
    path('chairperson/attendance-change-requests/approve/<int:request_id>/', views.approve_attendance_change_request_chairperson, name='approve_attendance_change_request_chairperson'),
    path('chairperson/attendance-change-requests/reject/<int:request_id>/', views.reject_attendance_change_request_chairperson, name='reject_attendance_change_request_chairperson'),

    # Admin Chairperson Management URLs
    path('dashboard/admin/manage-chairpersons/', views.manage_chairpersons, name='manage_chairpersons'),
    path('dashboard/dean/manage-chairpersons/', views.dean_manage_chairpersons, name='dean_manage_chairpersons'),
    path('dashboard/dean/remove-chairperson/<int:chairperson_id>/', views.dean_remove_chairperson, name='dean_remove_chairperson'),
    path('dashboard/admin/edit-chairperson/<int:chairperson_id>/', views.edit_chairperson, name='edit_chairperson'),
    path('dashboard/admin/remove-chairperson/<int:chairperson_id>/', views.remove_chairperson, name='remove_chairperson'),
    path('dashboard/admin/approve-chairperson/<int:chairperson_id>/', views.approve_chairperson, name='approve_chairperson'),

    # Controller Management URLs
    path('dashboard/admin/manage-controllers/', controller_views.manage_controllers, name='manage_controllers'),
    path('dashboard/admin/remove-controller/<int:controller_id>/', controller_views.remove_controller, name='remove_controller'),
    path('dashboard/controller/', controller_views.controller_dashboard, name='controller_dashboard'),

    # Unified Login and Registration
    path('login/', views.unified_login, name='unified_login'),
    path('register/selection/', views.registration_selection, name='registration_selection'),
    path('register/student/', views.student_register, name='student_register'),
    path('register/teacher/', views.register_teacher, name='register_teacher'),
    path('dashboard-selection/', views.dashboard_selection, name='dashboard_selection'),

    # AJAX endpoints for dropdowns
    path('ajax/get-programs-by-department/', views.get_programs_by_department, name='get_programs_by_department'),
    path('ajax/get-semesters-by-program/', views.get_semesters_by_program, name='get_semesters_by_program'),
    path('get-courses-by-semester/', views.get_courses_by_semester, name='get_courses_by_semester'),

    # Dynamic dropdown endpoints
    path('ajax/get-programs-by-department/<int:department_id>/', views.get_programs_by_department, name='get_programs_by_department'),
    path('ajax/get-semesters-by-program/<int:program_id>/', views.get_semesters_by_program, name='get_semesters_by_program'),

    # Admin attendance change request management
    path('dashboard/admin/attendance-change-requests/', views.attendance_change_requests_admin, name='attendance_change_requests_admin'),
    path('dashboard/admin/attendance-change-requests/approve/<int:request_id>/', views.approve_attendance_change_request, name='approve_attendance_change_request'),
    path('dashboard/admin/attendance-change-requests/reject/<int:request_id>/', views.reject_attendance_change_request, name='reject_attendance_change_request'),

    # Add these URL patterns to urlpatterns
    path('ajax/get-course-dates/<int:course_id>/', views.get_course_dates, name='get_course_dates'),
    path('ajax/get-course-students/<int:course_id>/<str:date>/', views.get_course_students, name='get_course_students'),
    path('ajax/get-attendance-status/<int:course_id>/<str:date>/<int:student_id>/', views.get_attendance_status, name='get_attendance_status'),
    path('mark-notification-read/', views.mark_notification_read, name='mark_notification_read'),
    path('mark-all-notifications-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/', views.view_all_notifications, name='view_all_notifications'),

    # Dean URLs
    path('dashboard/dean/', dean_views.dean_dashboard, name='dean_dashboard'),
    path('dashboard/admin/appoint-dean/', views.appoint_dean, name='appoint_dean'),
    path('dashboard/admin/remove-dean/<int:dean_id>/', views.remove_dean, name='remove_dean'),
    path('dashboard/dean/review-request/<int:request_id>/', views.review_chairperson_request, name='review_chairperson_request'),
    path('ajax/get-department-teachers/', views.get_teachers_by_department, name='get_department_teachers'),

    # Dean Attendance Summary URLs
    path('dean/attendance/summary/', dean_views.dean_attendance_summary, name='dean_attendance_summary'),
    path('dean/attendance/export/csv/', dean_views.dean_export_attendance_csv, name='dean_export_attendance_csv'),
    path('dean/attendance/export/pdf/', dean_views.dean_export_attendance_pdf, name='dean_export_attendance_pdf'),

    # Controller URLs
    path('controller/dashboard/', controller_views.controller_dashboard, name='controller_dashboard'),
    path('controller/attendance-summary/', controller_views.controller_attendance_summary, name='controller_attendance_summary'),
    path('controller/attendance/report/', controller_views.controller_attendance_report, name='controller_attendance_report'),
    path('controller/export-attendance-csv/', controller_views.controller_export_attendance_csv, name='controller_export_attendance_csv'),
    path('controller/export-attendance-pdf/', controller_views.controller_export_attendance_pdf, name='controller_export_attendance_pdf'),
    path('controller/admit-card-requests/', admit_card_views.view_admit_card_requests, name='view_admit_card_requests'),
    path('controller/admit-card-requests/approve/<int:request_id>/', admit_card_views.approve_admit_card_request, name='approve_admit_card_request'),
    
    # Controller AJAX endpoints
    path('controller/get-programs-by-department/<int:department_id>/', controller_views.get_programs_by_department, name='controller_get_programs'),
    path('controller/get-semesters-by-program/<int:program_id>/', controller_views.get_semesters_by_program, name='controller_get_semesters'),

    # API Endpoints
    path('api/courses/', views.get_courses, name='get_courses'),

    # Student URLs
    path('student/request-admit-card/', admit_card_views.request_admit_card, name='request_admit_card'),

    # Dean URLs for admit card requests
    path('dean/admit-card-requests/', admit_card_views.view_admit_card_requests, name='view_admit_card_requests'),
    path('dean/admit-card-requests/approve/<int:request_id>/', admit_card_views.approve_admit_card_request, name='approve_admit_card_request'),
]


