from model.chain import get_embeddings, start_conversation, process_input
from time import sleep
import redis
from dotenv import load_dotenv
import os

import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

load_dotenv()
redis_url = os.getenv("REDISCLOUD_URL")
r = redis.Redis.from_url(redis_url)

buldings_names = {
    "Alameda dos Nobres": "alameda_dos_nobres",
    "Antonio e Julia": "antonio_julia",
    "Capiba - Síndico": "capiba_sindico",
    "Capiba - Proprietário": "capiba_proprietario",
    "Mirante do Frio": "mirante_frio",
    "Test": "test",
}


def bot(prompt, phone_number, user_data):
    # user_data pode ser string (prédio único) ou lista (múltiplos prédios)

    # Tenta recuperar prédio escolhido do Redis
    current_building = r.get(f"user_session:{phone_number}")
    if current_building:
        current_building = current_building.decode("utf-8")

    # Se usuário tem vários prédios e não escolheu ainda
    if isinstance(user_data, list) and not current_building:
        # Tenta interpretar o prompt como índice
        try:
            idx = int(prompt)
            if 0 <= idx < len(user_data):
                chosen_building = user_data[idx]
                r.set(
                    f"user_session:{phone_number}", chosen_building, ex=900
                )  # expira em 15 min
                return (
                    f"Ok, vamos falar sobre o empreendimento {chosen_building}. "
                    "Caso deseje trocar de empreendimento mais tarde, basta digitar 'novo empreendimento'. "
                    "O que deseja saber?"
                )
            else:
                return (
                    "Número inválido. Por favor, escolha um dos números abaixo:\n"
                    + "\n".join(f"{i}: {b}" for i, b in enumerate(user_data))
                )
        except ValueError:
            # Não conseguiu converter para int, pede para escolher
            return (
                "Olá! Vimos que você tem acesso a vários empreendimentos. Qual deseja consultar? Responda com o número:\n"
                + "\n".join(f"{i}: {b}" for i, b in enumerate(user_data))
            )

    # Se usuário digitar 'novo empreendimento', limpa sessão para ele escolher outro
    if prompt.lower() == "novo empreendimento":
        r.delete(f"user_session:{phone_number}")
        if isinstance(user_data, list):
            return "Por favor, escolha o número do empreendimento:\n" + "\n".join(
                f"{i}: {b}" for i, b in enumerate(user_data)
            )
        else:
            # Se só tem um prédio, só informa
            return f"Você só tem acesso ao empreendimento {user_data}. Continue sua pergunta."

    # Aqui usuário já tem prédio definido (ou só tem um prédio)
    building = current_building if current_building else user_data

    try:
        insert_name_prompt = f"Você está respondendo sobre o edifício {building}.\n\n"
        # Chama função que processa a pergunta para aquele prédio
        prompt = insert_name_prompt + prompt
        resposta = process_input(prompt, buldings_names[building], phone_number)
        return resposta
    except Exception as e:
        logger.error(f"Erro ao processar a entrada: {e}")
        return (
            "Desculpe, tive um problema ao processar sua pergunta. Entre em contato com o suporte"
            " ou tente novamente mais tarde."
        )
