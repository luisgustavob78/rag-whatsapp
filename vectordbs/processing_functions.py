from azure.identity import AzureCliCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient

from dotenv import load_dotenv

import time
import re

from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader

import os

load_dotenv()

document_intelligence_endpoint = "https://tratto-doc-intel.cognitiveservices.azure.com/"
document_intelligence_key = os.getenv("DOCUMENT_INTELLIGENCE_KEY")


def get_chunks(text):
    headers_to_split_on = [("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3")]

    text_splitter = MarkdownHeaderTextSplitter(headers_to_split_on)

    text_chunks = text_splitter.split_text(text)
    return text_chunks


def get_embeddings(docs, batch_size=10):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

    for i in range(0, len(docs), batch_size):
        batch_docs = docs[i : i + batch_size]

        if i == 0:
            vector_storage = FAISS.from_documents(
                documents=batch_docs, embedding=embeddings
            )
        else:
            vector_storage.add_documents(documents=batch_docs)

        time.sleep(10)  # Pode ser ajustado se necessário por limites da API

    return vector_storage


def clean_extracted_text(text: str) -> str:
    # Remove blocos <figure> e ![]() de imagens
    text = re.sub(r"<figure>.*?</figure>", "", text, flags=re.DOTALL)
    text = re.sub(r"!\[\]\(.*?\)", "", text)

    # Remove comentários HTML do tipo <!-- ... -->
    text = re.sub(r"<!--.*?-->", "", text)

    # Remove excesso de quebras de linha e espaços
    text = re.sub(r"\n\s*\n", "\n\n", text)
    text = re.sub(r" +", " ", text)

    # Remove repetições genéricas de rodapés
    patterns_to_remove = [
        "MANUAL DO PROPRIETÁRIO",
        "Facilitat Tecnologia - Empresa do grupo Tecomat Engenharia",
        "EDIFÍCIO VALE DO AVE CAPIDA",
    ]
    for pattern in patterns_to_remove:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # Substitui "Tabela" por "### Tabela"
    text = re.sub(r"\bTabela\b", "### Tabela", text)

    return text.strip()


def extract_raw_text_from_docs(docs):
    print(len(docs), " docs loaded")
    raw_text = "".join([doc.page_content for doc in docs])
    return clean_extracted_text(raw_text)


def get_pdf_content(document):
    loader = AzureAIDocumentIntelligenceLoader(
        file_path=document,
        api_key=document_intelligence_key,
        api_endpoint=document_intelligence_endpoint,
        api_model="prebuilt-layout",
    )
    docs = loader.load()
    raw_text = extract_raw_text_from_docs(docs)

    return raw_text
