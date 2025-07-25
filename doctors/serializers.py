import json
from rest_framework import serializers
from django.contrib.auth import get_user_model
from core.models import User
from patients.models import Appointment 
from .models import Doctor, Prescription

user = get_user_model()

class DoctorRegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True) 
    first_name = serializers.CharField(write_only=True) 
    last_name = serializers.CharField(write_only=True) 

    class Meta:
        model = Doctor
        exclude = ['user']

    def create(self, validated_data):
        username = validated_data.pop('username')
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role='doctor'
        )
        
        doctor = Doctor.objects.create(user=user, **validated_data)
        return doctor

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = user
        fields =('id', 'username', 'first_name', 'last_name', 'email', 'role', 'is_active')
    
class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Doctor
        fields = ('id', 'user', 'specialization', 'phone', 'qualification', 'experience_years', 'license_number', 'consultation_fee', 'available_from', 'available_to')

class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = ['id', 'patient_name', 'doctor_name', 'scheduled_at', 'prescription_given', 'status']
        
    def get_patient_name(self, obj):
        return obj.patient.user.get_full_name()
    
    def get_doctor_name(self, obj):
        return obj.doctor.user.get_full_name()
    
    def get_status(self, obj):
        return not obj.status
    
class PrescriptionSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)
    patient_name = serializers.CharField(source='patient.user.get_full_name', read_only=True)
    medications = serializers.JSONField()
    medications_details = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Prescription
        fields = ['id', 'appointment', 'patient', 'patient_name', 'doctor', 'doctor_name', 'medications', 'medications_details', 'created_at', 'is_paid']
        read_only_fields = ['doctor', 'created_at', 'is_paid', 'doctor_name', 'patient_name', 'patient']

    def get_medications_details(self, obj):
        user = self.context['request'].user if self.context.get('request') else None
        if hasattr(user, 'doctor') or obj.is_paid:
            
            try:
                return json.loads(obj.medications)
            except Exception:
                return []
        else:
            return 'Prescription available after payment'

    def validate(self, attrs):
        if Prescription.objects.filter(appointment=attrs['appointment']).exists():
            raise serializers.ValidationError("A prescription already exists for this appointment.")
        return attrs


    def validate_medications(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Medications must be a list.")
        
        for med in value:
            if not isinstance(med, dict):
                raise serializers.ValidationError('Each medication must be a dictionary')
            if 'name' not in med or 'dosage' not in med:
                raise serializers.ValidationError('Each medication must have "name" and "dosage" mentioned')
        
        return value

    def create(self, validated_data):
        medications = validated_data.pop('medications')
        validated_data['medications'] = json.dumps(medications)
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        medications = validated_data.pop('medications', None)
        if medications is not None:
            validated_data['medications'] = json.dumps(medications)
        return super().update(instance, validated_data)