import spacy
import os
import re
import json
import logging

# Configuração do logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')

logging.info("Iniciando processamento de textos...")

def process_and_chunk():
    """
    Carrega o texto bruto da LGPD, o limpa e o divide em chunks estruturados
    baseados nos artigos e capítulos da lei.
    """

    # --- MODELO SPACY ---
    logging.info("Carregando modelo Spacy...")
    nlp = spacy.load("pt_core_news_lg", # modelo de tamanho gande e suporte pt
                     disable=["parser", "ner"]) 

    # Definindo a localização de entrada e saída do arquivo
    RAW_DATA_PATH = os.path.join("..", "data", "raw", "lgpd_raw.txt")
    PROCESSED_DATA_PATH = os.path.join("..", "data", "processed", "lgpd_chunks.json")

    logging.info(f"Lendo dados brutos de: {RAW_DATA_PATH}")
    with open(RAW_DATA_PATH, 'r', encoding='utf-8') as f:
        raw_text = f.read()

    # --- LIMPEZA DOS DADOS ---
    logging.info("Iniciando processo de limpeza dos dados...")
    processed_text = re.sub(r'\n+', '\n', raw_text).strip()
    processed_text = re.sub(r' +', ' ', processed_text)
    logging.info("Texto bruto processado com sucesso.")

    # --- CHUNKS ESTRUTURADOS ---
    logging.info("Estruturando o texto em 'chunks'...")
    pattern = r'(Art\.\s\d+°?\.?|CAPÍTULO\s[IVXLCDM]+)'
    parts = re.split(pattern, processed_text)

    chunks = []
    for i in range(1, len(parts), 2):
        chunk_title = parts[i].strip()
        chunk_text = (parts[i] + parts[i+1]).strip()
        chunks.append({
            'id': len(chunks),
            'source': chunk_title,
            'text': chunk_text})

    logging.info(f"Texto dividido em {len(chunks)} chunks estruturados.")

    # --- SALVA TEXTO PROCESSADO ---
    os.makedirs(os.path.dirname(PROCESSED_DATA_PATH), exist_ok=True)
    with open(PROCESSED_DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=4)
    
    logging.info(f"Chunks salvos com sucesso em: {PROCESSED_DATA_PATH}")

if __name__ == '__main__':
    process_and_chunk()
