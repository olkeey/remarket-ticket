from datetime import datetime
from typing import Any, Optional, List, Union
from pydantic import BaseModel


class CreateChatProfile(BaseModel):
    fullname: str | None
    phone:str | None 
    cpf: str | None
    passport: str | None
    pix_key:str | None 
    pix_key_type:str | None 
    accepted_terms_of_service_and_use: bool | None 
    accepted_terms_of_privacy:bool | None
    accepted_cookies_policy: bool | None



class TalkToOlavim(BaseModel):
    msg: str
    phone: str



from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReMKTVenueSchema(BaseModel):
    venue_type: str
    venue_name: str
    category: Optional[str]
    location: Optional[str]
    open_gates: Optional[datetime]

    class Config:
        orm_mode = True

class ReMKTItemClassSchema(BaseModel):
    remkt_venue_id: Optional[int]
    item_name: str
    sector_name: str
    genre: str
    remkt_original_vendor_id: Optional[int]

    class Config:
        orm_mode = True

class ReMKTOriginalVendorSchema(BaseModel):
    name: str
    is_enabled: Optional[bool] = True

    class Config:
        orm_mode = True

class ReMKTItemOfferInstanceSchema(BaseModel):
    remkt_item_class_id: Optional[int]
    offered_by_id: Optional[int]
    original_price: int
    current_price: int
    receive_method: str
    status: Optional[str] = "available"

    class Config:
        orm_mode = True

class ReMKTItemDemandInstanceSchema(BaseModel):
    remkt_item_class_id: Optional[int]
    demanded_by_id: Optional[int]
    original_price: int
    current_price: int
    status: Optional[str] = "searching"

    class Config:
        orm_mode = True


ItemInfoSchema = Union[ReMKTItemOfferInstanceSchema, ReMKTItemDemandInstanceSchema]