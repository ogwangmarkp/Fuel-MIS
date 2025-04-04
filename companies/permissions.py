from rest_framework import permissions

class IsPostOnly(permissions.BasePermission):
    """
        Object-level permission to only allow post 
    """

    def has_permission(self, request, view):
        if request.method == 'POST':
            return True
