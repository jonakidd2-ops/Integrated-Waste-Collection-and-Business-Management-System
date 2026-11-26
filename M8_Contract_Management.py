from datetime import date


class ContractManagementError(Exception):
    """Base exception for M8 errors."""


class ValidationError(ContractManagementError):
    """Raised when supplied customer or contract information is invalid."""


class CustomerNotFoundError(ContractManagementError):
    """Raised when a customer cannot be found."""


class ContractNotFoundError(ContractManagementError):
    """Raised when a contract cannot be found."""


class DocumentNotFoundError(ContractManagementError):
    """Raised when a supplied document ID does not exist."""


class ContractManagement:
    """Business logic for customer and contract management."""


    CUSTOMER_TABLE = "customers"
    CONTRACT_TABLE = "contracts"
    DOCUMENT_TABLE = "documents"

    def __init__(self, database):
        """
        Receive the Database object created by the C4 data access module.

        Example:
            db = Database("waste_management.db")
            m8 = ContractManagement(db)
        """
        if database is None:
            raise ValueError("A Database object from the data access module is required.")

        self.db = database

# THIS SECTION DEALS WITH VALIDATION METHODS

    @staticmethod
    """This text is at the least required, cannot continue without it."""
    def _required_text(value, field_name):
        """Return trimmed text or raise an error if it is missing."""
        if not isinstance(value, str) or not value.strip():
            raise ValidationError(f"{field_name} is required.")
        return value.strip()

    @staticmethod
    def _optional_text(value, field_name):
        """Return trimmed optional text."""
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} must be text.")
        return value.strip() or None

    @staticmethod
    def _valid_date(value, field_name):
        """Validate a date supplied in YYYY-MM-DD format."""
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} must use YYYY-MM-DD format.")
        
        try:
            return date.fromisoformat(value)
        except ValueError:
            raise ValidationError(
                f"{field_name} must be a valid date in YYYY-MM-DD format."
            ) from None


# THIS SECTION DEALS WITH CUSTOMERS AND CONTRACTS
    
    def create_customer(self, name, contact=None):
        """
        Store a new customer and return its generated database ID.
        The schema stores their name and one general contact field.
        """
        name = self._required_text(name, "Customer name")
        contact = self._optional_text(contact, "Customer contact")

        # The database also enforces UNIQUE on customers.name.
        existing = self.db.find(self.CUSTOMER_TABLE, name=name)
        if existing:
            raise ValidationError(f"Customer '{name}' already exists.")
    
        # Find the customer first so the contract uses the correct foreign key.
        customer = self.find_customer_by_name(customer_name)
        if customer is None:
            raise CustomerNotFoundError(
                f"Customer '{customer_name}' was not found. "
                "Create the customer before adding a contract."
            )

        # document_id is optional, but if supplied it must refer to a pre-existing document.

        if document_id is not None:
            self._validate_id(document_id, "Document ID")
            document = self.db.get(self.DOCUMENT_TABLE, document_id)

            if document is None:
                raise DocumentNotFoundError(
                    f"Document ID {document_id} does not exist."
                )
      
        """Details may include service arrangements, collection frequency and agreed fees 
        which do not have their own dedicated section"""
        
        contract_record = {
            "customer_id": customer["id"],
            "details": details,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "document_id": document_id,
        }

        with self.db.transaction():
            contract_id = self.db.save(
                self.CONTRACT_TABLE,
                contract_record,
            )

        return contract_id

    def get_contract(self, contract_id):
        """Retrieve one customer's contract using its database ID."""
        self._validate_id(contract_id, "Contract ID")
        return self.db.get(self.CONTRACT_TABLE, contract_id)

    def get_customer_contracts(self, customer_id):
        """Retrieves every contract of one particular customer using their customer ID."""
        self._validate_id(customer_id, "Customer ID")

        customer = self.db.get(self.CUSTOMER_TABLE, customer_id)
        """ensures customer exists"""
        if customer is None:
            raise CustomerNotFoundError(
                f"Customer ID {customer_id} does not exist."
            )

        return self.db.find(
            self.CONTRACT_TABLE,
            customer_id=customer_id,
        )

    def get_contracts_by_customer_name(self, customer_name):
        """Retrieves contracts by the customer's exact name."""
        customer = self.find_customer_by_name(customer_name)

        if customer is None:
            raise CustomerNotFoundError(
                """ensures customer exists"""
                f"Customer '{customer_name}' was not found."
            )

        return self.get_customer_contracts(customer["id"])

    def get_all_contracts(self):
        """Retrieve all contracts stored in the database."""
        return self.db.find(self.CONTRACT_TABLE)

    def get_contract_with_customer(self, contract_id):
        """
        Retrieve a contract together with its customer's name and contact.

        Uses the C4 query() method for the JOIN; M8 does not open a
        separate database connection.
        """
        self._validate_id(contract_id, "Contract ID")

        sql = """
            SELECT
                contracts.id,
                contracts.customer_id,
                customers.name AS customer_name,
                customers.contact AS customer_contact,
                contracts.details,
                contracts.start_date,
                contracts.end_date,
                contracts.document_id
            FROM contracts
            INNER JOIN customers
                ON contracts.customer_id = customers.id
            WHERE contracts.id = ?
        """

        results = self.db.query(sql, (contract_id,))
        return results[0] if results else None

# Code that is resused for validating customer/contract ID rather than rewriting for each method

    @staticmethod
    def _validate_id(value, field_name):
        """Require a database ID that is positive integer."""
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValidationError(f"{field_name} must be a positive integer.")

