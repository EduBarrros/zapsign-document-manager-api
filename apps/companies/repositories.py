from django.utils import timezone
from .models import Company
 
class CompanyRepository:
 
    def get_active_for_user(self, user):
        return Company.objects.filter(user=user, deleted_at__isnull=True)
 
    def belongs_to_user(self, company, user):
        return company.user_id == user.id
 
    def soft_delete(self, company):
        company.deleted_at = timezone.now()
        company.save(update_fields=["deleted_at"])
        return company
 
    def create(self, **data):
        return Company.objects.create(**data)
 