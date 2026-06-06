from .models import Company
from .repositories import CompanyRepository


class CompanyService:
    def __init__(self, repository: CompanyRepository | None = None):
        self.repository = repository or CompanyRepository()

    def soft_delete(self, company: Company) -> Company:
        return self.repository.soft_delete(company)
