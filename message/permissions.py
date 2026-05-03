from rest_framework.permissions import BasePermission


class HasRole(BasePermission):
    allowed_roles = []

    def has_permission(self, request, view):
        user_role = getattr(request.user, "role", None)
        if user_role is None:
            return False
        return (
            request.user
            and request.user.is_authenticated
            and str(user_role).lower() in self.allowed_roles
        )


class IsClient(HasRole):
    allowed_roles = ["client"]


class IsFreelancer(HasRole):
    allowed_roles = ["freelancer"]


class IsAdmin(HasRole):
    allowed_roles = ["admin"]
