from django.core.exceptions import PermissionDenied

class OwnerRequiredMixin:
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.author != self.request.user:
            raise PermissionDenied("Вы не автор этого объявления.")
        return obj