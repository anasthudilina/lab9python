from pydantic import BaseModel, Field

class ClientCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)

class AccountCreate(BaseModel):
    account_number: str = Field(min_length=5, max_length=50)
    client_id: int = Field(gt=0)
    initial_balance: float = Field(ge=0)

class AccountResponse(BaseModel):
    id: int
    account_number: str
    balance: float
    account_type: str
    client_id: int
    
    model_config = {"from_attributes": True}

class TransactionResponse(BaseModel):
    id: int
    amount: float
    operation_type: str
    account_id: int
    
    model_config = {"from_attributes": True}

class AmountRequest(BaseModel):
    amount: float = Field(gt=0, description="Amount must be greater than 0")

class TransferRequest(BaseModel):
    from_account: str
    to_account: str
    amount: float = Field(gt=0)

class AccountUpdate(BaseModel):
    account_type: str = Field(min_length=3, max_length=20)