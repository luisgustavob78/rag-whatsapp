from dotenv import load_dotenv
import numpy as np

from model.chain import get_embeddings, start_conversation, process_input
from src.utils import bot

import asyncio
import os

import json

from openai import OpenAI
from time import sleep
from flask import Flask, jsonify, request
import requests

import redis

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Inicializamos o Flask.
app = Flask(__name__)
app.secret_key = "bobassistente"

# Carregamos nossas variaveis de ambiente.
load_dotenv()

# Whatsapp API
token = os.getenv("TOKEN")
mytoken = os.getenv("MYTOKEN")

# Get redis connection
redis_url = os.getenv("REDISCLOUD_URL")
r = redis.Redis.from_url(redis_url)


@app.route("/webhook", methods=["GET"])
def webhook_verification():
    mode = request.args.get("hub.mode")
    challenge = request.args.get("hub.challenge")
    token = request.args.get("hub.verify_token")

    if mode and token:
        if mode == "subscribe" and token == mytoken:
            return challenge, 200
        else:
            return "", 403


def sendWhatsapp(phon_no_id, from_user, texto_resposta):
    global token
    url = f"https://graph.facebook.com/v22.0/{phon_no_id}/messages?access_token={token}"

    data = {
        "messaging_product": "whatsapp",
        "to": from_user,
        "text": {"body": texto_resposta},
    }

    headers = {"Content-Type": "application/json"}

    print(token)
    print(phon_no_id)
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        print("Mensagem enviada com sucesso!")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar mensagem: {e}")
        print(f"Resposta da API: {response.text}")


@app.route("/webhook", methods=["POST"])
def chat():
    try:
        body_param = request.json
        logging.info("Incoming webhook:\n" + json.dumps(body_param, indent=2))

        # Garante que é um webhook válido do WhatsApp
        if body_param.get("object") == "whatsapp_business_account":
            entry = body_param.get("entry", [])[0]
            changes = entry.get("changes", [])[0]
            value = changes.get("value", {})
            messages = value.get("messages")

            # Só processa se houver mensagens
            if messages and isinstance(messages, list):
                message = messages[0]
                phon_no_id = value.get("metadata", {}).get("phone_number_id")
                from_user = message.get("from")
                msg_body = message.get("text", {}).get("body")

                user_data_raw = r.hget("users_dict", from_user)
                user_data = (
                    json.loads(user_data_raw) if user_data_raw else "Desconhecido"
                )

                logging.info(f"Mensagem recebida de {from_user}: {msg_body}")
                texto_resposta = bot(
                    prompt=msg_body, phone_number=from_user, user_data=user_data
                )
                logging.info(f"Resposta: {texto_resposta}")

                sendWhatsapp(phon_no_id, from_user, texto_resposta)

                return jsonify({"status": "success"}), 200
            else:
                logging.info(
                    "Webhook recebido sem mensagem de usuário (provavelmente status como 'delivered')"
                )
                return jsonify({"status": "ignored"}), 200

        return jsonify({"status": "invalid"}), 400

    except Exception as erro:
        logging.error("Erro no processamento da mensagem", exc_info=True)
        return f"Erro: {erro}", 500
