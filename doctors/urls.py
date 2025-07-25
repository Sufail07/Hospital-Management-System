from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DoctorRegistrationView, DoctorPatientViewSet, MedicalHistoryViewSet, PrescriptionViewSet, get_logged_in_doctor, schedule


router = DefaultRouter()

router.register(r'patients', DoctorPatientViewSet, basename='view-patients')
router.register(r'medicalhistory', MedicalHistoryViewSet, basename='medical-history')
router.register(r'prescription', PrescriptionViewSet, basename='prescription')

urlpatterns = [
    path('register/', DoctorRegistrationView.as_view(), name='register-doctor'),
    path('appointments/', schedule, name='doctor-schedule'),
    path('me/', get_logged_in_doctor, name='logged-doctor'),
]

urlpatterns += router.urls



