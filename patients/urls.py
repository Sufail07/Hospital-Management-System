from django.urls import path, include
from patients.views import AppointmentViewSet, RegisterPatientView, PatientViewSet, MedicalHistoryViewSet, ViewDoctorsViewset, create_checkout_session, get_logged_in_patient, get_payments, payment_cancel, payment_success
from rest_framework.routers import DefaultRouter
from doctors.views import PrescriptionViewSet

router = DefaultRouter() 

router.register(r'patient', PatientViewSet, basename='admin-patient')
router.register(r'appointments', AppointmentViewSet, basename='admin-appointment')
router.register(r'medicalhistory', MedicalHistoryViewSet, basename='admin-medicalhistory')
router.register(r'doctors', ViewDoctorsViewset, basename='doctors')
router.register(r'prescriptions', PrescriptionViewSet, basename='admin-prescriptions')


urlpatterns = [
    path('register/', RegisterPatientView.as_view(), name='register_patient'),
    path('pay/prescription/<int:prescription_id>/', create_checkout_session, name='checkout-prescription'),
    path('payment-success/<int:prescription_id>/', payment_success, name='payment-success'),
    path('payment-cancel/<int:prescription_id>/', payment_cancel, name='payment-cancel'),
    path('payments/', get_payments, name='get-payments'),
    path('me/', get_logged_in_patient, name='logged-patient')
]

urlpatterns += router.urls
