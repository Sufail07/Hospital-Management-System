from django.db import models
from core.models import User
# Create your models here.

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    address = models.TextField()
    phone = models.CharField(max_length=15)
    emergency_contact = models.CharField(max_length=15, null=True, blank=True)

    blood_group = models.CharField(max_length=3, choices=[
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-')
    ], null=True, blank=True)
    
    date_registered = models.DateTimeField(auto_now_add=True)
    insurance_provider = models.CharField(max_length=25, blank=True)
    insurance_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f'{self.user.get_full_name()} ({self.user.username})'
    
class MedicalHistory(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_history')
    diagnosis = models.TextField()
    medications = models.TextField()
    allergies = models.TextField()
    recorded_by = models.ForeignKey('doctors.Doctor', on_delete=models.SET_NULL, null=True)
    recorded_at = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']

    def __str__(self):
        return f'Medical History of patient - {self.patient.user.username}'

class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey('doctors.Doctor', on_delete=models.CASCADE)
    scheduled_at = models.DateTimeField()
    prescription_given = models.BooleanField(default=False)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.patient.user.get_full_name()} - {self.doctor.user.get_full_name()}'
    
    