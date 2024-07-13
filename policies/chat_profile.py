from src.notification.policies.whatsapp_number_formatter import WhatsappNumberFormatter
from src.ticket_remarket.models import ReMKTChatProfile
from src.user_or_company_profile import services as user_profile_n_cia_services


class ChatProfileService:
    
   
    async def fetch_or_create_chat_profile(self,db,phone):
        

        chat_profile = db.query(ReMKTChatProfile).filter(ReMKTChatProfile.phone == phone, ReMKTChatProfile.status == "active").first()
        if not chat_profile:
            chat_profile = await self.create_new_chat_profile(db, fullname=None, phone=phone)
        return chat_profile
    
    async def create_new_chat_profile(self, db, 
                                fullname, 
                                phone, 
                                cpf=None, 
                                passport=None, 
                                pix_key=None, 
                                pix_key_type=None, 
                                accepted_terms_of_service_and_use=False, 
                                accepted_terms_of_privacy=False, 
                                accepted_cookies_policy=False):
       

        profile = await self.fetch_profile_by_user_phone(db=db, phone=self.format_whatsapp_number(phone))
        profile_id = None
        if profile:
            pix_key = profile.pix_key
            pix_key_type = profile.pix_key_type
            fullname = f"{profile.first_name} {profile.last_name}"
            profile_id = profile.id
            if profile.cpf:
                cpf = profile.cpf
            elif profile.passport:
                passport = passport

            accepted_terms_of_service_and_use = profile.accepted_terms_of_service_and_use
            accepted_terms_of_privacy = profile.accepted_terms_of_privacy
            accepted_cookies_policy = profile.accepted_cookies_policy

        new_profile = ReMKTChatProfile(
            fullname=fullname,
            user_profile_id = profile_id if profile_id else None,
            phone=phone,
            cpf=cpf,
            passport=passport,
            pix_key=pix_key,
            pix_key_type=pix_key_type,
            accepted_terms_of_service_and_use=accepted_terms_of_service_and_use,
            accepted_terms_of_privacy=accepted_terms_of_privacy,
            accepted_cookies_policy=accepted_cookies_policy
        )
        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)
        return new_profile

   

    def format_whatsapp_number(self, phone):
        
        if phone.startswith("whatsapp:"):
            phone = phone.replace("whatsapp:", "")
        if phone.startswith("+55") and len(phone) == 13:
            phone = phone[:5] + "9" + phone[5:]
        print(phone)
        return phone

    # async def fetch_or_create_chat_profile(self,db,phone):Zz
    #     wapp_formatter = WhatsappNumberFormatter()
    #     phone = wapp_formatter.format_number_for_saving(phone)

    #     return db.query(ReMKTChatProfile).filter(ReMKTChatProfile.phone == phone, ReMKTChatProfile.status == "active").first()

    async def fetch_profile_by_user_phone(self, db, phone):
        return user_profile_n_cia_services.fetch_user_profile_by_phone(db=db, phone=phone)
