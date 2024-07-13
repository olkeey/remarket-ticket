import datetime
from typing import Any
from sqlalchemy.orm import Session
from src.ticket_remarket import models as ticket_remarket_models


class ChatSessionProcessor:
     
    @staticmethod
    async def get_active_chat_session_or_create_new(db: Session, available_info_chat_profile: Any):
        """
        Get an active chat session along with its formatted messages, or create a new session if none exists.
        """
        chat_session = await ChatSessionProcessor.get_chat_session(db, available_info_chat_profile.id)
        if not chat_session:
            chat_session = await ChatSessionProcessor.create_new_chat_session(db, available_info_chat_profile.id)
            

        messages = await ChatSessionProcessor.get_chat_messages(db, chat_session,available_info_chat_profile)
        


        return {
            "chat_session": chat_session,
            "messages": messages
        }
   
    @staticmethod
    async def get_chat_session(db: Session, chat_profile_id: int):
        """
        Fetch the chat session by ID if it is active.
        """
        return db.query(ticket_remarket_models.ReMKTChatSession).filter(ticket_remarket_models.ReMKTChatSession.chat_profile_id == chat_profile_id, ticket_remarket_models.ReMKTChatSession.status == 'active').first()

    @staticmethod
    async def create_new_chat_session(db: Session, chat_profile_id: int):
        """
        Create a new chat session with status 'first_message'.
        """
        new_chat_session = ticket_remarket_models.ReMKTChatSession(
            created_at=datetime.datetime.now(),
            status='first_message',
            chat_profile_id=chat_profile_id
        )
        db.add(new_chat_session)
        db.commit()
        return new_chat_session


    @staticmethod
    async def get_chat_messages(db: Session, chat_session: int, available_chat_profile: Any):
        """
        Fetch all messages related to the given chat session ID.
        """
        messages = db.query(ticket_remarket_models.ReMKTChatMessages).filter_by(chat_session_id=chat_session.id).all()
        
        if not messages:
            return [await ChatSessionProcessor.init_system_message(db, chat_session, available_chat_profile)]
        return ChatSessionProcessor.format_messages(messages)
    
    @staticmethod
    async def init_system_message(db, chat_session, available_chat_profile):
        content = ""
        user_content = ChatSessionProcessor.get_user_info_content(available_chat_profile)
        chat_session_content = ChatSessionProcessor.get_chat_session_content(chat_session)
        content = user_content + chat_session_content
        system_init_message = {
                "role": "system",
                "content": content
            }
        formatted_message = ticket_remarket_models.ReMKTChatMessages(
                sent_by=1,  # 1 for system
                chat_session_id=chat_session.id,
                content=system_init_message["content"]
            )
        db.add(formatted_message)
        db.commit()
        return system_init_message
    
    @staticmethod
    def get_chat_session_content(chat_session):
        message_content = f"Chat session info: Session ID: {chat_session.id} Started at: {chat_session.created_at} Last message: {chat_session.last_message} Chat profile ID: {chat_session.chat_profile_id} Status: {chat_session.status}. "
        return message_content

    
    @staticmethod
    def get_user_info_content(chat_available_info):
        content = ""
        content += f"Você está conversando com {chat_available_info.fullname if chat_available_info.fullname else 'Não coletamos ainda o nome completo dessa pessoa, '}"
        content+= f"Com telefone {chat_available_info.phone}. "
        content+= f"CPF: {chat_available_info.cpf if chat_available_info.cpf else 'Não coletado' }, Passaporte: {chat_available_info.passport if chat_available_info.passport else 'Não coletado'}, "
        content+= f"chave PIX: {chat_available_info.pix_key if chat_available_info.pix_key else 'Não coletado'} (tipo: {chat_available_info.pix_key_type if chat_available_info.pix_key_type else 'Não coletado'}). "
        content+= "Se você inferir que o usuário não é brasileiro, você fala muito bem inglês e como você ama idiomas, vai tentar se comunicar na língua nativa do usuário, mas cometa erros não impactantes e diga que está aprendendo a língua, inclusive tente ser divertido e alegre ded ter a oportunidade de exercitar esse idioma que não é português. Talvez tente saber mais sobre de onde mais especificamente a pessoa é originada e conte alguma curiosidade que você sabe sobre o local, ou apenas seja positivo sobre onde a pessoa vive, mas nunca cometa discriminação étnica em comentários. Se a pessoa optar por seguir a conversa em inglês mesmo, ou português atenda ao pedido."
        return content

    @staticmethod
    def format_message(message):
        """
        Format a single message to the required format.
        """
        role_mapping = {1: "system", 2: "user", 3: "assistant", 4: "function"}
        role = role_mapping.get(message.sent_by, "unknown")
        return {
            "role": role,
            "content": message.content
        }

    @staticmethod
    def format_messages(messages):
        """
        Format a list of messages to the required format.
        """
        print(messages)
        return [ChatSessionProcessor.format_message(message) for message in messages]

   
