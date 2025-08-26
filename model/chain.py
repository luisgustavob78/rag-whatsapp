from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path

from model.prompt import SYSTEM_PROMPT, CONTEXTUALIZE_PROMPT

import numpy as np

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.messages import BaseMessage
from langchain_core.runnables.history import RunnableWithMessageHistory

import os
import redis
import logging

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
redis_url = os.getenv("REDISCLOUD_URL")


def get_embeddings(vectordb_name: str = "default") -> FAISS:
    """
    Load the FAISS vector store with OpenAI embeddings.

    Args:
        vectordb_name (str, optional): The name of tha vector database
        to be loaded. Defaults to "default".

    Returns:
        FAISS: FAISS vector store loaded with OpenAI embeddings.
    """
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large", openai_api_key=openai_api_key
    )

    base_dir = Path(__file__).resolve().parent
    vector_storage = FAISS.load_local(
        f"{base_dir}/vector_storage/vector_embeddings_{vectordb_name}",
        embeddings=embeddings,
        allow_dangerous_deserialization=True,
    )
    return vector_storage


def get_llm() -> ChatOpenAI:
    """
    Function that instantiates the LLM with the given parameters.

    Returns:
        ChatOpenAI: Instance of the ChatOpenAI class with the specified model and temperature.
    """
    return ChatOpenAI(model="gpt-4o", temperature=0.1, openai_api_key=openai_api_key)


# def start_conversation(vector_embeddings):
def retrieve_context(vector_embeddings: FAISS) -> RunnableWithMessageHistory:
    """
    Retrieve context from the vector embeddings using a history-aware retriever.

    Args:
        vector_embeddings (FAISS): Vector store containing embeddings for retrieval.

    Returns:
        RunnableWithMessageHistory: Retrieved documents related to the input query with chat history.
    """
    contextualize_q_prompt = ChatPromptTemplate(
        [
            ("system", CONTEXTUALIZE_PROMPT),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    history_aware_retriever = create_history_aware_retriever(
        get_llm(), vector_embeddings.as_retriever(k=3), contextualize_q_prompt
    )

    return history_aware_retriever


def get_rag_chain(vector_embeddings: FAISS) -> RunnableWithMessageHistory:
    """
    Creates a Retrieval-Augmented Generation (RAG) chain using the provided vector embeddings.

    Args:
        vector_embeddings (FAISS): Vector store containing embeddings for retrieval.

    Returns:
        RunnableWithMessageHistory: A runnable chain that combines retrieval and question-answering capabilities.
    """
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(get_llm(), qa_prompt)
    rag_chain = create_retrieval_chain(
        retrieve_context(vector_embeddings), question_answer_chain
    )

    return rag_chain


def start_conversation(vector_embeddings: FAISS) -> RunnableWithMessageHistory:
    """
    Starts a conversation chain with message history using the provided vector embeddings.

    Args:
        vector_embeddings (FAISS): Vector store containing embeddings for retrieval.

    Returns:
        RunnableWithMessageHistory: A runnable chain that manages conversation history and
        retrieval-augmented generation.
    """

    def get_session_history(session_id: str) -> RedisChatMessageHistory:
        return RedisChatMessageHistory(session_id=session_id, url=redis_url)

    # ✅ Limit messages using `trim_messages`
    def trim_last_k_messages(
        messages: list[BaseMessage], k: int = 3
    ) -> list[BaseMessage]:
        return messages[-k:]

    conversational_rag_chain = RunnableWithMessageHistory(
        get_rag_chain(vector_embeddings),
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
        trim_messages=lambda messages: trim_last_k_messages(messages, k=5),
    )

    return conversational_rag_chain


def process_input(query: str, building_name: str, session_id: str = None) -> str:
    """
    This functions processes the input from the user, calls the vector embeddings
    according to the phone number to retrieve information about the right building, and
    then generates the answer calling the LLM API.

    Args:
        query (str): User's input question or request.
        building_name (str): Building's name, used to retrieve the right vector embeddings.
        session_id (_type_, optional): ID for session memory using user's number. Defaults to None.

    Returns:
        str: Generated answer from the LLM based on the user's input and context.
    """
    vector_embeddings = get_embeddings(building_name)
    chain = start_conversation(vector_embeddings)

    response = chain.invoke(
        {"input": query}, config={"configurable": {"session_id": session_id}}
    )

    return response["answer"]
