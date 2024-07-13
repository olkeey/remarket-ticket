from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from src.ticket_remarket import models
from src.ticket_remarket import schemas
def register_item(db: Session, venue_info: schemas.ReMKTVenueSchema, vendor_info: schemas.ReMKTOriginalVendorSchema, item_class_info: schemas.ReMKTItemClassSchema, item_info:schemas.ItemInfoSchema, item_type: str):
    # Check and get or create venue
    try:
        venue = db.query(models.ReMKTVenue).filter_by(venue_name=venue_info['venue_name']).one()
    except NoResultFound:
        venue = models.ReMKTVenue(**venue_info)
        db.add(venue)
        db.commit()

    # Check and get or create vendor
    try:
        vendor = db.query(models.ReMKTOriginalVendor).filter_by(name=vendor_info['name']).one()
    except NoResultFound:
        vendor = models.ReMKTOriginalVendor(**vendor_info)
        db.add(vendor)
        db.commit()

    # Check and get or create item class
    try:
        item_class = db.query(models.ReMKTItemClass).filter_by(
            remkt_venue_id=venue.id, 
            item_name=item_class_info['item_name'],
            sector_name=item_class_info['sector_name'],
            genre=item_class_info['genre'],
            remkt_original_vendor_id=vendor.id
        ).one()
    except NoResultFound:
        item_class = models.ReMKTItemClass(
            remkt_venue_id=venue.id,
            item_name=item_class_info['item_name'],
            sector_name=item_class_info['sector_name'],
            genre=item_class_info['genre'],
            remkt_original_vendor_id=vendor.id
        )
        db.add(item_class)
        db.commit()

    # Save offer or demand item based on item_type
    if item_type == "offer":
        offer_item = models.ReMKTItemOfferInstance(
            offered_by_id=item_info['offered_by_id'],
            original_price=item_info['original_price'],
            current_price=item_info['current_price'],
            receive_method=item_info['receive_method'],
            status=item_info['status'],
        )
        db.add(offer_item)
    elif item_type == "demand":
        demand_item = models.ReMKTItemDemandInstance(
            original_price=item_info['original_price'],
            current_price=item_info['current_price'],
            demanded_by_id=item_info['demanded_by_id'],
            status=item_info['status'],
        )
        db.add(demand_item)
    
    db.commit()