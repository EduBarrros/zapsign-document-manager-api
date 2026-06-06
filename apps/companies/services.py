from .repositories import CompanyRepository

class CompanyService:
    def __init__(self, repository=None):
        self.repository = repository or CompanyRepository()

    def get_active_for_user(self, user):
        return self.repository.get_active_for_user(user)

    def create_company(self, user, **data):
        return self.repository.create(user=user, **data)

    def soft_delete(self, company):
        return self.repository.soft_delete(company)