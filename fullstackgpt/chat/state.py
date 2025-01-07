import reflex as rx
import sqlmodel

from datetime import datetime, timezone
from typing import List, Optional
from fullstackgpt.models import ChatSession, ChatSessionMessageModel
from . import ai


class ChatMessage(rx.Base):
    message: str
    is_bot: bool = False


class ChatState(rx.State):
    chat_session: ChatSession = None
    did_submit: bool = False
    messages: List[ChatMessage] = []
    not_found: Optional[bool] = None

    @rx.var
    def user_did_submit(self) -> bool:
        return self.did_submit

    def get_session_id(self) -> int:
        try:
            my_session_id = int(self.router.page.params.get("session_id"))
        except:
            my_session_id = None
        return my_session_id

    def create_new_chat_session(self):
        """Crea una nueva sesión de chat en la base de datos."""
        try:
            with rx.session() as db_session:
                # Crear nueva sesión con título por defecto
                new_session = ChatSession(
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                
                # Agregar y hacer commit
                db_session.add(new_session)
                db_session.commit()
                db_session.refresh(new_session)
                
                self.chat_session = new_session
                return new_session
                
        except Exception as e:
            print(f"❌ Error al crear nueva sesión: {str(e)}")
            # No propagar el error, pero asegurarse de que el estado sea consistente
            self.chat_session = None
            return None

    def insert_message_to_db(self, content: str, role: str = "user"):
        """Inserta un mensaje en la base de datos."""
        if not self.chat_session or not isinstance(self.chat_session, ChatSession):
            print("❌ No hay sesión activa para guardar el mensaje")
            return None
            
        try:
            with rx.session() as db_session:
                # Crear nuevo mensaje
                new_message = ChatSessionMessageModel(
                    session_id=self.chat_session.id,
                    content=content,
                    role=role,
                    created_at=datetime.now(timezone.utc)
                )
                
                # Agregar y hacer commit
                db_session.add(new_message)
                db_session.commit()
                db_session.refresh(new_message)
                
                #print(f"✅ Mensaje guardado con ID: {new_message.id}")
                return new_message
                
        except Exception as e:
            print(f"❌ Error al guardar mensaje: {str(e)}")
            return None

    def clear_ui(self):
        self.chat_session = None
        self.not_found = None
        self.did_submit = False
        self.messages = []

    def crete_new_and_redirect(self):
        self.clear_ui()
        new_session = self.create_new_chat_session()
        return rx.redirect(f'/chat/ {new_session.id} ')

    def clear_and_start_new(self):
        self.clear_ui()
        self.create_new_chat_session()
        yield

    def get_session_from_db(self, session_id=None):
        """
        Recupera una sesión de chat de la base de datos y carga sus mensajes.
        
        Args:
            session_id (int, optional): ID de la sesión a recuperar. 
                                      Si no se proporciona, se obtiene de la URL.
        """
        try:
            # Obtener session_id si no se proporcionó
            if session_id is None:
                session_id = self.get_session_id()
                
            with rx.session() as db_session:
                # Consultar la sesión
                sql_statement = sqlmodel.select(ChatSession).where(
                    ChatSession.id == session_id
                )
                result = db_session.exec(sql_statement).one_or_none()
                
                # print(f"Engine URL: {db_session.get_bind().url}")
                # print(f"Database: {db_session.get_bind().url.database}")
                # print(f"Host: {db_session.get_bind().url.host}")
                
                # Manejar caso de sesión no encontrada
                if result is None:
                    self.not_found = True
                    print("❌ Sesión no encontrada")
                    return
                
                # Actualizar estado con la sesión encontrada
                self.not_found = False
                self.chat_session = result
                
                # Cargar mensajes en la UI
                self.messages = []  # Limpiar mensajes existentes
                for message in result.messages:
                    is_bot = message.role != "user"
                    self.append_message_to_ui(message.content, is_bot=is_bot)
                
             
        except Exception as e:
            print(f"❌ Error al cargar la sesión: {str(e)}")
            self.not_found = True
            return

    def on_detail_load(self):
        session_id = self.get_session_id()
        reload_detail= False
        if not self.chat_session:
            reload_detail = True
        else:
            if self.chat_session.id != session_id:
                reload_detail = True
                
        if reload_detail:
            self.clear_ui()
            if isinstance(session_id, int):
                self.get_session_from_db(session_id=session_id)

    def on_load(self):
        self.clear_ui()
        self.create_new_chat_session()



    def append_message_to_ui(self, message, is_bot=False):
        self.messages.append(ChatMessage(message=message, is_bot=is_bot))

    def gpt_messages(self):
        gpt_messages = [
            {
                "role": "system",
                "content": "eres un experto español creando recetas como un chef de elite. Responde en español y en makdown",
            }
        ]

        for chat_message in self.messages:
            role = "user"
            if chat_message.is_bot:
                role = "assistant"
            gpt_messages.append({"role": role, "content": chat_message.message})

        return gpt_messages

    async def handle_submit(self, form_data: dict):
        user_message = form_data.get("message")
        if user_message:
            self.did_submit = True
            self.append_message_to_ui(user_message, is_bot=False)
            self.insert_message_to_db(user_message, role="user")
            yield
            gpt_messages = self.gpt_messages()
            bot_response = ai.get_llm_response(gpt_messages)
            #bot_response = "respuesta del bot"
            self.did_submit = False
            if isinstance(bot_response, str):
                self.append_message_to_ui(bot_response, is_bot=True)
                self.insert_message_to_db(bot_response, role="System")
            yield
