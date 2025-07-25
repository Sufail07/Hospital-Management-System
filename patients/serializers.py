from rest_framework import serializers
from doctors.serializers import PrescriptionSerializer
from core.models import User
from doctors.models import Doctor, Payment, Prescription
from .models import Appointment, MedicalHistory, Patient
from django.contrib.auth import get_user_model

user = get_user_model()

class RegisterPatientSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    email = serializers.CharField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)

    class Meta:
        model = Patient
        fields = ['username', 'password', 'email', 'first_name', 'last_name', 'date_of_birth', 'gender', 'address', 'phone', 'emergency_contact', 'blood_group', 'insurance_provider', 'insurance_number']

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        email = validated_data.pop('email')
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role='patient'
        )
        
        patient = Patient.objects.create(user=user, **validated_data)
        return patient

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = user
        fields =('id', 'username', 'first_name', 'last_name', 'email', 'role', 'is_active')

class PatientSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Patient
        fields = ['id', 'email', 'user', 'username', 'full_name', 'date_of_birth', 'gender', 'address', 'phone', 'emergency_contact', 'blood_group', 'insurance_provider', 'insurance_number', 'date_registered']   

class AppointmentSerializer(serializers.ModelSerializer):
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(),
        source='doctor',
        write_only=True
    )
    doctor = serializers.StringRelatedField(read_only=True)
    patient = serializers.StringRelatedField(read_only=True)
    scheduled_at = serializers.DateTimeField()
    prescription_given = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = ['id', 'doctor_id', 'patient', 'doctor', 'scheduled_at', 'prescription_given']
        
    def get_prescription_given(self, obj):
        return Prescription.objects.filter(appointment=obj).exists()
        
class MedicalHistorySerializer(serializers.ModelSerializer):
    patient_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = MedicalHistory
        fields = '__all__'
        read_only_fields = ['recorded_by', 'recorded_at', 'patient']

class PaymentSerializer(serializers.ModelSerializer):
    prescription = PrescriptionSerializer()

    class Meta:
        model = Payment
        fields = ['id', 'amount', 'status', 'created_at', 'prescription']