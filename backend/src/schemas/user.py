from pydantic import BaseModel, EmailStr
from datetime import datetime
from pydantic import ConfigDict




class UserBase(BaseModel):
    email: EmailStr
    name: str | None = None
    phone_number: str | None = None


    
    
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    phone_number: str | None = None
    name: str | None = None
    
    
    
class UserRead(UserBase):
    id: int 
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
    
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str