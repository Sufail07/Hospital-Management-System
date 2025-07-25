from django.shortcuts import get_object_or_404, render
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from django.utils.dateparse import parse_date
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Doctor, Prescription
from patients.models import Appointment, MedicalHistory, Patient
from patients.serializers import MedicalHistorySerializer, PatientSerializer
from patients.permissions import IsDoctorOrReadOnlyForPatients
from .serializers import AppointmentSerializer, DoctorRegistrationSerializer, DoctorSerializer, PrescriptionSerializer
# Create your views here.


class DoctorRegistrationView(CreateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorRegistrationSerializer
    permission_classes = [AllowAny]
    
class MedicalHistoryViewSet(ModelViewSet):
    queryset = MedicalHistory.objects.all()
    permission_classes = [IsAuthenticated, IsDoctorOrReadOnlyForPatients]
    serializer_class = MedicalHistorySerializer

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'doctor'):
            patient_ids = Appointment.objects.filter(doctor__user=user).values_list('patient', flat=True).distinct()
            return MedicalHistory.objects.filter(patient__id__in=patient_ids)
        elif hasattr(user, 'patient'):
            return MedicalHistory.objects.filter(patient__user=user)
        return MedicalHistory.objects.none()

    @action(detail=True, methods=['get'], url_path='patient-history')
    def patient_history(self, request, pk=None):
        try:
            patient = Patient.objects.get(id=pk)
        except Patient.DoesNotExist:
            return Response({'message': 'Patient not found'})
        
        histories = MedicalHistory.objects.filter(patient=patient)
        serializer = self.get_serializer(histories, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        user = self.request.user
        if hasattr(user, 'doctor') and 'patient_id' in self.request.data:
            patient = Patient.objects.get(id=self.request.data['patient_id'])
            serializer.save(recorded_by=user.doctor, patient=patient)
        else:
            return serializers.ValidationError('Only doctors can add medical history, and patient_id is required')


class DoctorPatientViewSet(ReadOnlyModelViewSet):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'doctor':
            patient_ids = Appointment.objects.filter(doctor__user=user).values_list('patient', flat=True).distinct()
            return Patient.objects.filter(id__in=patient_ids)
        raise PermissionDenied("Only doctors can view patients.")


@api_view(['GET'])
def schedule(request):
    if request.user.role == 'doctor' and request.user.is_authenticated:
        appointments = Appointment.objects.select_related('patient__user').filter(doctor__user=request.user)
        date_str = request.GET.get('date')
        if date_str:
            filter_date = parse_date(date_str)
            if filter_date:
                appointments = appointments.filter(scheduled_at__date=filter_date)
                
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)
    return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)


class PrescriptionViewSet(ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'doctor'):
            return Prescription.objects.filter(doctor__user=user)
        elif hasattr(user, 'patient'):
            return Prescription.objects.filter(patient__user=user)
        else:
            raise PermissionDenied('Only doctors and patients can view prescriptions')
        
    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'doctor':
            appointment_id = self.request.data.get('appointment')
            appointment = get_object_or_404(Appointment, id=appointment_id)
            if appointment.doctor != user.doctor:
                raise PermissionDenied('You are not assigned to this appointment')
            prescription = serializer.save(doctor=user.doctor, appointment=appointment, patient=appointment.patient, diagnosis=self.request.data.get('diagnosis', 'Not specified'))
            appointment.prescription_given = True
            appointment.status = True
            appointment.save()
            
            # creating medical history for the patient along with the creation of a presciption
            MedicalHistory.objects.create(
                patient=appointment.patient, diagnosis=prescription.diagnosis, medications=prescription.medications, recorded_by=user.doctor, allergies='Not specified'
            )
            
        else:
            raise PermissionDenied('Only doctors can create Prescriptions')

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_logged_in_doctor(request):
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        return Response({'error': 'Patient not found'}, status=404) 
    
    serializer = DoctorSerializer(doctor)
    return Response(serializer.data)
