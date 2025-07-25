from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminDoctorViewSet, AllAppointmentViewSet, AllPatientsViewSet, AllPrescriptionViewSet, get_dashboard_stats, get_logged_in_admin, grant_access_doctor, grant_access_patient, revoke_access_doctor, revoke_access_patient
from patients.views import MedicalHistoryViewSet

router = DefaultRouter()
router.register(r'doctor', AdminDoctorViewSet, basename='admin-doctors')
router.register(r'patient', AllPatientsViewSet, basename='admin-patients')
router.register(r'appointment', AllAppointmentViewSet, basename='admin-appointments')
router.register(r'prescription', AllPrescriptionViewSet, basename='admin-prescriptions')
router.register(r'medicalhistory', MedicalHistoryViewSet, basename='admin-medicalhistory')

urlpatterns = [
    path('me/', get_logged_in_admin, name='logged-admin'),
    path('dashboard/stats/', get_dashboard_stats, name='dashboard-stats'),
    path('revoke_access_patient/<int:patient_id>/', revoke_access_patient, name='revoke-patient'),
    path('grant_access_patient/<int:patient_id>/', grant_access_patient, name='grant-patient'),
    path('revoke_access_doctor/<int:doctor_id>/', revoke_access_doctor, name='revoke-doctor'),
    path('grant_access_doctor/<int:doctor_id>/', grant_access_doctor, name='grant-doctor'),
]

urlpatterns += router.urls
