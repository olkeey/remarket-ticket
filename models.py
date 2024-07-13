from datetime import datetime
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID
import uuid
import pytz
from src.database import Base

from sqlalchemy.orm import relationship, backref
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    ForeignKey,
    Table,
    Float,
    UniqueConstraint,
    func,
)

class ReMKTChatProfile(Base):
    __tablename__ = "remkt_chat_profile"
    id = Column(Integer, primary_key=True, index=True)
    user_profile_id = Column(Integer, ForeignKey("user_profile.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    fullname = Column(String)
    phone = Column(String, nullable=False)
    cpf = Column(String, nullable=True, unique=True)
    passport = Column(String, nullable=True, unique=True)
    pix_key = Column(String)
    pix_key_type = Column(String)
    accepted_terms_of_service_and_use = Column(Boolean, default=False) # must be shared
    accepted_terms_of_privacy = Column(Boolean, default=False)
    accepted_cookies_policy = Column(Boolean, default=False)
    status = Column(String, default="active") # blocked

### create member report

class ReMKTChatSession(Base):
    __tablename__ = "remkt_chat_session"
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_message = Column(DateTime(timezone=True))
    chat_profile_id = Column(Integer, ForeignKey("remkt_chat_profile.id"), nullable=True)
    status = Column(String) # finished, idle, active, order_complete_waiting_payout, order_complete_waiting_item_validation

class ReMKTChatMessages(Base):
    __tablename__ = "remkt_chat_message"
    id = Column(Integer, primary_key=True, index=True)
    sent_by = Column(Integer) # 1 role, 2 user, 3 system
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    chat_session_id = Column(Integer, ForeignKey("remkt_chat_session.id"), nullable=True)
    content = Column(String)

class ReMKTVenue(Base):
    __tablename__ = "remkt_venue"
    id = Column(Integer, primary_key=True, index=True)
    venue_type = Column(String, nullable=False, default="event")
    category = Column(String)
    location = Column(String) # this must be normalized
    venue_name = Column(String)
    open_gates =Column(DateTime(timezone=True))

class ReMKTItemClass(Base):
    __tablename__ = "remkt_item_class"
    id = Column(Integer, primary_key=True, index=True)
    remkt_venue_id = Column(Integer, ForeignKey("remkt_venue.id"), nullable=False)
    item_name = Column(String)
    sector_name = Column(String)
    genre = Column(String)
    remkt_original_vendor_id = Column(Integer, ForeignKey("remkt_original_vendor.id"), nullable=False)

class ReMKTOriginalVendor(Base):
    __tablename__= "remkt_original_vendor"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False) # ingresse, ticketmasters, eventim
    is_enabled=Column(Boolean) 


class ReMKTItemOfferInstance(Base):
    __tablename__ = "remkt_item_offer_instance"
    id = Column(Integer, primary_key=True, index=True)
    rkmt_item_class = Column(Integer, ForeignKey("remkt_item_class.id"), nullable=False)
    offered_by_id = Column(Integer, ForeignKey("remkt_chat_profile.id"), nullable=True)
    original_price =  Column(Integer,)
    current_price = Column(Integer,)
    receive_method = Column(String) # physical_customer_pickup, physical_merchant_delivers, digital_img_share, digital_wallet_transfer
    status = Column(String, default="available")

class ReMKTItemDemandInstance(Base):
    __tablename__ = "remkt_item_demand_instance"
    id = Column(Integer, primary_key=True, index=True)
    original_price =  Column(Integer,)
    rkmt_item_class = Column(Integer, ForeignKey("remkt_item_class.id"), nullable=False)
    current_price = Column(Integer,)
    demanded_by_id = Column(Integer, ForeignKey("remkt_chat_profile.id"), nullable=True)
    status = Column(String, default="searching")


class ReMKTNegotiation(Base):
    __tablename__ = "remkt_negotiation"
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="open")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ReMKTNegotiationItem(Base):
    __tablename__ = "remkt_negotiation_item"
    id = Column(Integer, primary_key=True, index=True)
    offer_item = Column(Integer, ForeignKey("remkt_item_offer_instance.id"), nullable=True)
    negotiated_price = Column(Integer)
    demand_item =Column(Integer, ForeignKey("remkt_item_demand_instance.id"), nullable=True)
    status = Column(String, default="open")
    order = Column(Integer, ForeignKey("order.id"), nullable=True)

class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.
    """

    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


class ReMKTOrder(Base):
    __tablename__ = "rmkt_order"
    id = Column(Integer, primary_key=True, autoincrement=True)
    # POSTGRESuuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # SQLite
    uuid = Column(GUID(), unique=True, default=lambda: str(uuid.uuid4()))
    ### THESE NEXT
    buyer_id = Column(Integer, nullable=False)
    merchant_id = Column(Integer, nullable=False)
    ## creating_order_items, validating_inventory, pending_payment, finished_reserve processing_payment, completed, failed, cancelled
    status = Column(
        String, default="waiting_for_payment", nullable=False
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(
        Integer, ForeignKey("user_profile.id"), nullable=True
    )  ## OFFLINE
    annotations = Column(
        String
    )  # OFFLINE notes (payment document serial, type of payment)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    consolidated_price = Column(Integer, nullable=True)
    payout_id = Column(Integer, ForeignKey("payout.id"), nullable=True)
    payout_compensation_status = Column(String)
    # programmed_payment_id = Column(Integer, ForeignKey("programmed_payment.id"))
    # programmed_payment = relationship("ProgrammedPayment", backref=backref("orders"))
    consolidated_olkeey_fee = Column(Integer, nullable=True, default=0)
    consolidated_merchant_cashback = Column(Integer, nullable=True, default=0)
    order_complete_email_sent = Column(Boolean, default=False)
    installment_costs = Column(Integer)
    # updated_by = Column(Integer)

class ReMKTPayment(Base):
    __tablename__ = "remkt_payment"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("order.id"))
    payment_type = Column(Integer, nullable=False)
    payment_id = Column(Integer, nullable=False)  # payment intent
    status = Column(String, nullable=False, default="processing")
    created_at = Column(DateTime(timezone=True), server_default=func.now())