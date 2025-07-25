from django.db import models
from django.db.models import JSONField
from patients.models import Appointment, Patient
from core.models import User
# Create your models here.


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    qualification = models.CharField(max_length=150, blank=True)
    experience_years = models.IntegerField(default=0)
    license_number = models.CharField(max_length=50, unique=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    available_from = models.TimeField(null=True, blank=True)
    available_to = models.TimeField(null=True, blank=True)
    
    def __str__(self):
        return f'Dr. {self.user.get_full_name()} - {self.specialization}'



class Prescription(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    diagnosis = models.TextField(default='Not Specified')
    medications = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    
    def __str__(self):
        return f'Meds prescribed for {self.patient.user.get_full_name()} by Dr. {self.doctor.user.get_full_name()}'
        

class Payment(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('paid', 'Paid')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Payment for {self.prescription.patient.user.username}'