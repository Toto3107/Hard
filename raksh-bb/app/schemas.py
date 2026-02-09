from pydantic import BaseModel, EmailStr, constr


# ---------- Auth ----------

class UserCreate(BaseModel):
    email: EmailStr
    password: constr(min_length=8, max_length=128)
    full_name: str | None = None


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None = None
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int | None = None


# ---------- Borewells ----------

class BorewellBase(BaseModel):
    latitude: float
    longitude: float


class BorewellCreate(BorewellBase):
    pass

class PredictionRequest(BaseModel):
    latitude: float
    longitude: float


class PredictionResponse(BaseModel):
    latitude: float
    longitude: float
    predicted_feasible: bool
    predicted_depth_m: float
    model_version: str


class BorewellUpdateOutcome(BaseModel):
    actual_feasible: bool
    actual_depth_m: float


class BorewellOut(BorewellBase):
    id: int
    predicted_feasible: bool
    predicted_depth_m: float
    model_version: str
    actual_feasible: bool | None = None
    actual_depth_m: float | None = None

    class Config:
        from_attributes = True
