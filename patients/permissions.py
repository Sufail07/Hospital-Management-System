from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsPatient(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'patient'


class IsDoctorOrReadOnlyForPatients(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'doctor':
            return True

        elif user.role == 'admin':
            return True
        
        elif user.role == 'patient' and request.method in SAFE_METHODS:
            return obj.patient.user == user
        
        return False
        
    
