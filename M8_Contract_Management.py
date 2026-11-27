#M8 Contracts (F-06): customer information and contract details.

#every operation checks the user's role through M2 (M2_Security), and the errors
#inherit from the shared ServiceError so the screens can show their messages.

#this is hoe you make stuff with the funcs.
#m8 = ContractManagement(db)  # db is the M9 Database object
#cid = m8.create_customer(user, "Sunrise Hotel", "876-555-0100")
#m8.create_contract(user, "Sunrise Hotel", "Weekly pickup", "2026-01-01", "2026-12-31")

from datetime import date

from . import M2_Security
from .errors import NotFound, ServiceError, ValidationError  # ValidationError is shared


class ContractManagementError(ServiceError):
    """Base exception for M8 errors."""


class CustomerNotFoundError(ContractManagementError, NotFound):
    """Raised when a customer cannot be found."""


class ContractNotFoundError(ContractManagementError, NotFound):
    """Raised when a contract cannot be found."""


class DocumentNotFoundError(ContractManagementError, NotFound):
    """Raised when a supplied document ID does not exist."""


class ContractManagement:
    """Business logic for customer and contract management."""

    CUSTOMER_TABLE = "customers"
    CONTRACT_TABLE = "contracts"
    DOCUMENT_TABLE = "documents"
    PERMISSION = "M8_Contract_Management"   # key in M2_Security.PERMISSIONS (Owner, Admin)

    JOINE_D = (
        "SELECT contracts.id, contracts.customer_id, customers.name AS customer_name, "
        "customers.contact AS customer_contact, contracts.details, contracts.start_date, "
        "contracts.end_date, contracts.document_id "
        "FROM contracts INNER JOIN customers ON contracts.customer_id = customers.id"
    )

    def __init__(self, database):
        """Receive the Database object created by the C4 data access module (M9)."""
        if database is None:
            raise ValueError("A Database object from the data access module is required.")
        self.db = database

    # ---------------------------------------------------------
    # Validation helpers
    # ---------------------------------------------------------
    def _check_access(self, user):
        M2_Security.require(user, self.PERMISSION)

    @staticmethod
    def _required_text(value, field_name):
        if not isinstance(value, str) or not value.strip():
            raise ValidationError(f"{field_name} is required.")
        return value.strip()

    @staticmethod
    def _optional_text(value, field_name):
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} must be text.")
        return value.strip() or None

    @staticmethod
    def _valid_date(value, field_name):
        """Validate a date supplied in YYYY-MM-DD format and return a date object."""
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} must use YYYY-MM-DD format.")
        try:
            return date.fromisoformat(value.strip())
        except ValueError:
            raise ValidationError(f"{field_name} must be a valid date in YYYY-MM-DD format.") from None

    @staticmethod
    def _validate_id(value, field_name):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValidationError(f"{field_name} must be a positive integer.")

    def _check_document(self, document_id):
        """document_id is optional, but if supplied it must refer to an existing document."""
        if document_id is None:
            return
        self._validate_id(document_id, "Document ID")
        if self.db.get(self.DOCUMENT_TABLE, document_id) is None:
            raise DocumentNotFoundError(f"Document ID {document_id} does not exist.")

    def _contract_fields(self, customer_name, details, start_date, end_date, document_id):
        """Validate everything for a contract and return (customer, record fields)."""
        customer = self._customer_by_name(customer_name)
        if customer is None:
            raise CustomerNotFoundError(
                f"Customer '{str(customer_name).strip()}' was not found. "
                "Create the customer before adding a contract.")
        details = self._required_text(details, "Contract details")
        start = self._valid_date(start_date, "Start date")
        end = self._valid_date(end_date, "End date")
        if end < start:
            raise ValidationError("The end date cannot be before the start date.")
        self._check_document(document_id)
        return {"customer_id": customer["id"], "details": details,
                "start_date": start.isoformat(), "end_date": end.isoformat(),
                "document_id": document_id}

    def _customer_by_name(self, name):
        name = self._required_text(name, "Customer name")
        rows = self.db.find(self.CUSTOMER_TABLE, name=name)
        return rows[0] if rows else None

    # ---------------------------------------------------------
    # Customer operations
    # ---------------------------------------------------------
    def create_customer(self, user, name, contact=None):
        """Store a new customer and return its generated database ID."""
        self._check_access(user)
        name = self._required_text(name, "Customer name")
        contact = self._optional_text(contact, "Customer contact")
        if self.db.find(self.CUSTOMER_TABLE, name=name):       # the database also enforces UNIQUE
            raise ValidationError(f"Customer '{name}' already exists.")
        return self.db.save(self.CUSTOMER_TABLE, {"name": name, "contact": contact or ""})

    def find_customer_by_name(self, user, name):
        """Return the customer with this exact name, or None."""
        self._check_access(user)
        return self._customer_by_name(name)

    def list_customers(self, user):
        self._check_access(user)
        return self.db.find(self.CUSTOMER_TABLE)

    # ---------------------------------------------------------
    # Contract operations
    # ---------------------------------------------------------
    def create_contract(self, user, customer_name, details, start_date, end_date, document_id=None):
        """Store a contract for an existing customer and return its ID."""
        self._check_access(user)
        record = self._contract_fields(customer_name, details, start_date, end_date, document_id)
        with self.db.transaction():
            return self.db.save(self.CONTRACT_TABLE, record)

    def update_contract(self, user, contract_id, customer_name, details, start_date, end_date,
                        document_id=None):
        """Edit an existing contract."""
        self._check_access(user)
        self._validate_id(contract_id, "Contract ID")
        if self.db.get(self.CONTRACT_TABLE, contract_id) is None:
            raise ContractNotFoundError(f"Contract ID {contract_id} does not exist.")
        record = self._contract_fields(customer_name, details, start_date, end_date, document_id)
        record["id"] = contract_id
        with self.db.transaction():
            self.db.save(self.CONTRACT_TABLE, record)

    def get_contract(self, user, contract_id):
        """Retrieve one contract, with its customer's name and contact."""
        self._check_access(user)
        self._validate_id(contract_id, "Contract ID")
        rows = self.db.query(self.JOINE_D + " WHERE contracts.id = ?", (contract_id,))
        if not rows:
            raise ContractNotFoundError(f"Contract ID {contract_id} does not exist.")
        return rows[0]

    get_contract_with_customer = get_contract        # name used in the original version

    def get_customer_contracts(self, user, customer_id):
        """Retrieve every contract belonging to a particular customer."""
        self._check_access(user)
        self._validate_id(customer_id, "Customer ID")
        if self.db.get(self.CUSTOMER_TABLE, customer_id) is None:
            raise CustomerNotFoundError(f"Customer ID {customer_id} does not exist.")
        return self.db.query(self.JOINE_D + " WHERE contracts.customer_id = ? ORDER BY contracts.id",
                             (customer_id,))

    def get_contracts_by_customer_name(self, user, customer_name):
        """Retrieve contracts by the customer's exact name."""
        self._check_access(user)
        customer= self._customer_by_name(customer_name)
        if customer is None:
            raise CustomerNotFoundError(f"Customer '{customer_name.strip()}' was not found.")
        return self.get_customer_contracts(user, customer["id"])

    def get_all_contracts(self, user):
        self._check_access(user)
        return self.db.query(self.JOINE_D + " ORDER BY contracts.id DESC")

    def find_contracts(self, user, text=""):
        """Search by customer name or any words in the contract details (SR-06.x)."""
        self._check_access(user)
        if not text or not text.strip():
            return self.get_all_contracts(user)
        like=f"%{text.strip()}%"
        return self.db.query(
            self.JOINE_D + " WHERE customers.name LIKE ? OR contracts.details LIKE ? "
            "ORDER BY contracts.id DESC", (like, like))

