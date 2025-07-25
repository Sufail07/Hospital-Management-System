from django.shortcuts import get_object_or_404, render
from rest_framework.generics import CreateAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework import filters
from rest_framework.decorators import api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from adminpanel.models import Admin
from doctors.models import Doctor, Prescription
from doctors.serializers import AppointmentSerializer, DoctorRegistrationSerializer, DoctorSerializer, PrescriptionSerializer
from patients.models import Appointment, Patient
from patients.serializers import PatientSerializer
from .permissions import IsAdminUser, IsSuperUser
from .serializers import AdminRegistrationSerializer, AdminSerializer
from rest_framework.permissions import AllowAny

# Create your views here.

class AllAppointmentViewSet(ModelViewSet):
    queryset = Appointment.objects.select_related('doctor', 'patient').all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated, IsSuperUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['patient__user__username', 'doctor__user__username', 'scheduled_at']

class AllPrescriptionViewSet(ReadOnlyModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated, IsSuperUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['doctor', 'patient', 'is_paid']

class AdminDoctorViewSet(ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated, IsSuperUser]
    
    @action(detail=True, methods=['post'], url_path='revoke_access')
    def revoke_access(self, request, pk=None):
        doctor = get_object_or_404(Doctor, pk=pk)   
        if not doctor.is_active:
            return Response({'message': 'Doctor access is already revoked'}, status=status.HTTP_200_OK)
        
        doctor.is_active = False
        doctor.save()
        return Response({'message': f'Access revoked of doctor: {doctor.user.get_full_name()}'})
    
    @action(detail=True, methods=['post'], url_path='provide_access')
    def provide_access(self, request, pk=None):
        doctor = get_object_or_404(Doctor, pk=pk)
        if doctor.is_active:
            return Response({'message': 'Doctor access is already active'}, status=status.HTTP_200_OK)
        
        doctor.is_active = True
        doctor.save()
        return Response({'message': f'Access granted for doctor: {doctor.user.get_full_name()}'})
        
class AllPatientsViewSet(ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsSuperUser]


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsSuperUser])
def get_logged_in_admin(request):
    try:
        admin = Admin.objects.get(user=request.user)
    except Admin.DoesNotExist:
        return Response({'error': 'Admin not found'}, status=404) 

    serializer = AdminSerializer(admin)
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated, IsSuperUser])
def get_dashboard_stats(request):
    try:
        total_patients = Patient.objects.count()
        total_doctors = Doctor.objects.count()
        total_appointments = Appointment.objects.count()
        
        return Response({
            'totalPatients': total_patients,
            'totalDoctors': total_doctors,
            'totalAppointments': total_appointments
        })
    except Exception as e:
        return Response({'error': 'Failed to fetch stats'}, status=500)
    
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsSuperUser])
def revoke_access_doctor(request, doctor_id):
    try:
        doctor = get_object_or_404(Doctor, id=doctor_id)
        doctor.user.is_active = False
        doctor.user.save()
    except Doctor.DoesNotExist:
        return Response({'message': 'Doctor not found'}, status=404)
    
    return Response({'message': 'Doctor access successfully revoked'}, status=200)
    
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsSuperUser])
def revoke_access_patient(request, patient_id):
    try:
        patient = get_object_or_404(Patient, id=patient_id)
        patient.user.is_active = False
        patient.user.save()
    except Patient.DoesNotExist:
        return Response({'message': 'Patient not found'}, status=404)
    
    return Response({'message': 'Patient access successfully revoked'}, status=200)
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsSuperUser])
def grant_access_doctor(request, doctor_id):
    try:
        doctor = get_object_or_404(Doctor, id=doctor_id)
        doctor.user.is_active = True
        doctor.user.save()
    except Doctor.DoesNotExist:
        return Response({'message': 'Doctor not found'}, status=404)
    
    return Response({'message': 'Doctor access successfully granted'}, status=200)
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsSuperUser])
def grant_access_patient(request, patient_id):
    try:
        patient = get_object_or_404(Patient, id=patient_id)
        patient.user.is_active = True
        patient.user.save()
    except Patient.DoesNotExist:
        return Response({'message': 'Doctor not found'}, status=404)
    
    return Response({'message': 'Doctor access successfully revoked'}, status=200)
    