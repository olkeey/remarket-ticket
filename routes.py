import os
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Response
from src.ticket_remarket import schemas

from sqlalchemy.orm import Session
from src import database
from src.ticket_remarket.policies.chat_profile import ChatProfileService
from src.ticket_remarket.policies.chat_session_loader import ChatSessionProcessor
from src.ticket_remarket.policies.olavim_broker import OlavimBroker


router = APIRouter(
    prefix="/remarket-tickets",
    tags=["Remarket"],
)


@router.post("/",)
async def create_chat_profile(
    payload: schemas.CreateChatProfile,
    db: Session = Depends(database.get_db)):
    chat_profile_service = ChatProfileService()

    chat_profile = await chat_profile_service.fetch_chat_profile(phone=payload.phone, db=db)
    if chat_profile:
        return
    chat_profile = await chat_profile_service.create_new_chat_profile(db, 
                                                       fullname=payload.fullname, 
                                phone=payload.phone, 
                                cpf=payload.cpf, 
                                passport=payload.passport, 
                                pix_key=payload.pix_key, 
                                pix_key_type=payload.pix_key_type, 
                                accepted_terms_of_service_and_use=payload.accepted_terms_of_service_and_use, 
                                accepted_terms_of_privacy=payload.accepted_terms_of_privacy, 
                                accepted_cookies_policy=payload.accepted_cookies_policy
                                                       )
    print("finished")
    
    return



@router.post("/talk",)
async def create_chat_profile(
    payload: schemas.TalkToOlavim,
    db: Session = Depends(database.get_db)):
    
    chat_profile_service = ChatProfileService()
    chat_profile = await chat_profile_service.fetch_or_create_chat_profile(db, payload.phone)

    chat_session = await ChatSessionProcessor.get_active_chat_session_or_create_new(db,available_info_chat_profile=chat_profile)
    
    olavim = OlavimBroker()
    await olavim.start_olavim(chat_session["messages"],payload.msg, chat_session["chat_session"].id,)
    olavim_answer = await olavim.talk_to_olavim(db)
    if chat_session["chat_session"].status == "first_message":
        chat_session["chat_session"].status = "active"
        db.add(chat_session["chat_session"])
        db.commit
    return olavim_answer
    