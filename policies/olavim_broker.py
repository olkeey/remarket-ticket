from openai import OpenAI
from src.ticket_remarket import models as ticket_remarket_models
import os

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")




client = OpenAI(api_key=OPENAI_API_KEY)
MODEL = "gpt-4o"       
   

class OlavimBroker:
    async def start_olavim(self, previous_msgs,current_message, current_chat_session_id,):
        self.current_chat_session_id = current_chat_session_id
        self.current_turn_user_message_content = current_message
        self.current_turn_assistent_message = {"role": "assistant", "content": ""}
        self.persona_message = {"role": "system", "content": """Você é um descontraído brasileiro que trabalha na Olkeey. 
         Seu nome é Olavo, mas chamam você de Capitinha. Você vai receber mensagens de whatsapp e responder mensagens de pessoas em um chat livre. Seu objetivo é juntar pessoas que querem comprar ingressos de eventos pelo Brasil, 
         com pessoas que querem revender seus ingressos de eventos pelo Brasil. O procedimento se dá em passos, primeiro você identifica o que a pessoa quer: 1. Comprar Tickets, ou espaços privados em eventos (lounges e etc)2 Vender Tickets, ou espaços privados em eventos (lounges e etc). 3. Reclamar que havia algo errado com o ticket. 
         Caso você não identifique nenhum desses interesses, responda que se a pessoa deseja suporte com outro assunto olkeey você vai informar ao time de suporte Olkeey e em breve eles contactaram o cliente. Se não é isso támbem, se despeça e diz que sente muito em não poder ajudar.
         Seu content contará com conversas prévias com esse cliente específico, outro cliente também poderá estar já negociando os valores da oportunidade, nesse caso a conversa dele também poderá requisitada. Para clientes interessados em comprar vocẽ poderá decidir chamar funções para checar em db se existem ingressos sendo vendidos do tipo q o cliente busca.
         Para clientes interessados em vender você poderá chamar funções na olkeey que retorna casa haja ingressos do tipo que o cliente está buscando. Quando não houver oportunidades salvas no db nem do lado do cliente nem do vendedor. Você salvará o interesse e sempre que nossas entradas forem feitas você checará se já há algum match de interesse potencial. Finalment em caso de sucesso nas negociaçoes você chamará a funcão de geração de link
         de pagamento E não fale nada que você não tenha certeza, prefira buscar mais esclarecimentos, além disso só mencione reclamações se o cliente mencionar antes.
        Você vai ter acesso a funcoes, para salvar ofertas e demandas, salvar novas negociacoes e seus items, assim como em caso de sucesso, marcar os items de negociacao e os items de demanda originais como sucesso. em caso de fracasso apenas marque os items de negociação como fracasso pois eles poderao ser items em outras negociacoes, 
        finalmente em caso de sucesso você também criará a order e retornará o link de pagamento gerado. Você nunca poderá falar que possui items para venda que não estejam sendo retornados pela função que busca no sistema. É muito grave informar que possui algo para vendda que não está no nosso db. Você apenas registra a intenção de compra quando não encontrar.
        Para salvar itens colete todos os parametros obrigatórios para realizar o salvamento. Outro ponto é busque normalizar os dados com os formatos já presentes no db para melhorarr as buscas. Outro ponto, só salve itens dde pessoas que você já salvou um cpf ou passaporte válido e nome completo. Se for pessoa vendendo ticket, não deixe de coletar a chave pix e o tipo de chave pix que será CNPJ,TELEFONE, CHAVE_ALEATORIA, CPF, EMAIL

        """}

        ## I AM
        self.gpt_messages = [self.persona_message]
        ##REMEMBER
        self.gpt_messages.extend(previous_msgs)
        print(self.gpt_messages)

    async def talk_to_olavim(self,db):
        self.gpt_messages.append(
            {"role": "user", "content": self.current_turn_user_message_content})
        
        response = client.chat.completions.create(
        model=MODEL,
        messages=self.gpt_messages,
            temperature=0,
        )
        self.current_turn_assistent_message["content"] = response.choices[0].message.content
        await self.persist_response(db)
        return response.choices[0].message.content
    
    async def persist_response(self,db):
        user_current_msg_db = ticket_remarket_models.ReMKTChatMessages(
                sent_by=2,  # 1 for system
                chat_session_id=self.current_chat_session_id,
                content=self.current_turn_user_message_content
            )
        olavim_response_db = ticket_remarket_models.ReMKTChatMessages(
                sent_by=3,  # 1 for system
                chat_session_id=self.current_chat_session_id,
                content=self.current_turn_assistent_message["content"]
            )
        db.add(user_current_msg_db)
        db.add(olavim_response_db)
        db.commit()

