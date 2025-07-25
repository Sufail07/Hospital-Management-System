import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils.dateparse import parse_datetime
from rest_framework.viewsets import ModelViewSet, GenericViewSet, ReadOnlyModelViewSet
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework import status
from rest_framework.response import Response
from rest_framework import mixins
from doctors.models import Doctor, Payment, Prescription
from doctors.serializers import DoctorSerializer
from patients.permissions import IsDoctorOrReadOnlyForPatients, IsPatient
from .serializers import AppointmentSerializer, MedicalHistorySerializer, PatientSerializer, PaymentSerializer, RegisterPatientSerializer
from .models import Appointment, MedicalHistory, Patient
from rest_framework import serializers
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
# Create your views here.


class RegisterPatientView(CreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = RegisterPatientSerializer
    permission_classes = [AllowAny]

class ViewDoctorsViewset(ReadOnlyModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]

class PatientViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return get_object_or_404(Patient, user=self.request.user)
    

class AppointmentViewSet(ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated, IsPatient]

    def get_queryset(self):
        return self.queryset.filter(patient__user=self.request.user).exclude(prescription__isnull=False)

    def create(self, request, *args, **kwargs):
        doctor_id = request.data.get('doctor_id')
        scheduled_at = request.data.get('appointment_time')

        if not doctor_id or not scheduled_at:
            return Response({'message': 'doctor_id and appointment_time should be provided'}, status=status.HTTP_400_BAD_REQUEST)

        parsed_time = parse_datetime(scheduled_at)
        if not parsed_time:
            return Response({'message': 'Invalid appointment_time format'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            patient = Patient.objects.get(user=request.user)
        except Patient.DoesNotExist:
            return Response({'message': 'User is not a patient'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            doctor = Doctor.objects.get(id=doctor_id)
        except Doctor.DoesNotExist:
            return Response({'message': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)

        # Prevent scheduling conflicts
        if Appointment.objects.filter(doctor=doctor, scheduled_at=parsed_time).exists():
            return Response({'message': 'Appointment already exists at that time'}, status=409)
        
        appointment = Appointment.objects.create(
            patient = patient,
            doctor = doctor,
            scheduled_at = parsed_time
        )
        
        serializer = self.get_serializer(appointment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        new_time = request.data.get('scheduled_at')
        
        if new_time:
            parsed_time = parse_datetime(new_time)
            if not parsed_time:
                return Response({"message": "Invalid datetime format"}, status=400)
            
            # Prevent rescheduling conflicts
            if Appointment.objects.filter(doctor=instance.doctor, scheduled_at=parsed_time).exclude(id=instance.id).exists():
                return Response({'message': 'Doctor unavailable at that time'}, status=409)
            
            instance.scheduled_at = parsed_time
            instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class MedicalHistoryViewSet(ModelViewSet):
    queryset = MedicalHistory.objects.all()
    permission_classes = [IsAuthenticated, IsDoctorOrReadOnlyForPatients]
    serializer_class = MedicalHistorySerializer

    @action(detail=False, methods=['get'], url_path='patient/(?P<patient_id>[^/.]+)')
    def get_by_patient(self, request, patient_id=None):
        user = request.user
        if not hasattr(user, 'admin'):
            return Response({'detail': 'Only admins can access this endpoint.'}, status=403)
        queryset = MedicalHistory.objects.filter(patient__id=patient_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'doctor'):
            patient_ids = Appointment.objects.filter(doctor__user=user).values_list('patient', flat=True).distinct()
            
            patients = Patient.objects.filter(id__in=patient_ids)
            
            return MedicalHistory.objects.filter(patient__in=patients)
        elif hasattr(user, 'patient'):
            # Users can only access their own medical history
            return MedicalHistory.objects.filter(patient__user=user)
        
        elif hasattr(user, 'admin'):
            return MedicalHistory.objects.all()
        
        return MedicalHistory.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if not hasattr(user, 'doctor'):
            raise serializers.ValidationError('Only doctors can add medical history')
        
        patient_id = self.request.data.get('patient_id')
        if not patient_id:
            raise serializers.ValidationError('patient_id is required')
        
        # Only doctors that had previous appointments with the patient can create medical history for that patient
        try:
            patient = Patient.objects.get(id=patient_id)
            if Appointment.objects.filter(doctor=user.doctor, patient=patient).exists():
                serializer.save(recorded_by=user.doctor, patient=patient)
            else:
                raise serializers.ValidationError('The patient is not affiliated with the doctor')                
        except Patient.DoesNotExist:
            raise serializers.ValidationError('Invalid patient_id')
        
        

stripe.api_key = settings.STRIPE_SECRET_KEY
@csrf_exempt
def create_checkout_session(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id)

    total_cost_paise = 0
    description = []

    try:
        meds = json.loads(prescription.medications)
    except Exception:
        return JsonResponse({"error": "Invalid medications format"}, status=400)
    
    for med in meds:
        name = med.get('name', 'Unknown Medication')
        description.append(f'{name}')

    total_cost_paise = int(prescription.doctor.consultation_fee * 100)
    description.append(f'Consultation fee: ${prescription.doctor.consultation_fee}')

    if total_cost_paise == 0:
        return JsonResponse({"error": "Consultation fee has not been provided for the doctor"}, status=400)
    
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'inr',
                'unit_amount': total_cost_paise,
                'product_data': {
                    'name': f'Prescription #{prescription.id}',
                    'description': '\n'.join(description),
                },
            },
            'quantity': 1,       
        }],
        mode='payment',
        success_url=f'http://localhost:3000/patient/payment-success/?prescription_id={prescription_id}/',
        cancel_url=f'http://localhost:3000/patient/payment-cancel/?prescription_id={prescription_id}/',
        metadata={
            'prescription_id': str(prescription_id),
            'patient_id': str(prescription.patient.id),
        }
    )
    
    return JsonResponse({'checkout_session_id': session.id, 'checkout_url': session.url})

@api_view(['GET'])
@permission_classes([AllowAny])
def payment_success(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id)
    prescription.is_paid = True
    prescription.save()
    amount = prescription.doctor.consultation_fee
    Payment.objects.create(prescription=prescription, amount=amount, status='Paid')
    return Response({'message': 'Payment completed successfully'}, status=200)

@api_view(['GET'])
@permission_classes([AllowAny])
def payment_cancel(request, prescription_id):
    return JsonResponse({'status': 'cancelled', 'message': f'Payment was cancelled by the user for prescription_id: {prescription_id}'}, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsPatient])
def get_payments(request):
    try:
        patient = request.user.patient
    except AttributeError:
        return Response({'detail': 'Patient profile not found'}, status=400)
    
    payments = Payment.objects.filter(prescription__patient=patient).select_related('prescription')
    serializer = PaymentSerializer(payments, many=True)
    return Response(serializer.data)
        

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_logged_in_patient(request):
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        return Response({'error': 'Patient not found'}, status=404) 

    print('user: ', request.user)
    print('Is_authenticated: ', request.user.is_authenticated)
    serializer = PatientSerializer(patient)
    return Response(serializer.data)

