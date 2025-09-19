from ninja import Schema
from datetime import date
from typing import Optional
from enum import Enum

class ProfessionEnum(str, Enum):
    student = "student"
    law_practitioner = "law_practitioner"
    other = "other"

class LoginSchema(Schema):
    username :str
    password:str

class TokenSchema(Schema):
    access: str
    refresh : str

class SignupSchema(Schema):
    username : str
    password1 : str
    password2 : str
    email : str
    place : Optional[str] = None
    date_of_birth : Optional[date] = None
    profession : Optional[ProfessionEnum] = None
    mobile_no : Optional[str] = None