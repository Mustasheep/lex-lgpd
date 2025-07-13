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
    Versão 2.0:
    Carrega o texto bruto da LGPD, o limpa e o divide em chunks estruturados
    baseados nos artigos e capítulos da lei.
    
    Etapa 1: Divide o texto por Artigos/Capítulos
    Etapa 2: Subdivide os chunks anterior por incisos (I, II, III...)
    """

    # --- MODELO SPACY ---
    logging.info("Carregando modelo Spacy...")
    nlp = spacy.load("pt_core_news_lg",
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

    # --- ETAPA 1---
    logging.info("Estruturando o texto em 'chunks'...")
    primary_pattern = r'(CAPÍTULO\s[IVXLCDM]+\s*-|Art\.\s\d+º?\.?)'
    primary_chunks_raw = re.split(primary_pattern, processed_text)

    final_chunks = []
    chunk_id_count = 0
    for i in range(1, len(primary_chunks_raw), 2):
        primary_title = primary_chunks_raw[i].strip()
        primary_content = (primary_chunks_raw[i+1]).strip()

        # --- ETAPA 2 ---
        inciso_pattern = r'([IVXLCDM]+\s*-)'
        sub_chunks = re.split(inciso_pattern, primary_content)

        if len(sub_chunks) > 2:
            logging.info(f"Subdividindo '{primary_title}' em incisos...")
            caput_text = (primary_title + " " + sub_chunks[0]).strip()
            final_chunks.append({
                'id': chunk_id_count,
                'source': primary_title,
                'text': caput_text
            })
            chunk_id_count += 1

            # Agrupando os incisos
            for j in range(1, len(sub_chunks), 2):
                inciso_title = sub_chunks[j].strip()
                inciso_text = (sub_chunks[j] + sub_chunks[j+1]).strip()
                final_chunks.append({
                    'id': chunk_id_count,
                    'source': f"{primary_title}, Inciso {inciso_title.replace('-', '').strip()}",
                    'text': inciso_text
                })
                chunk_id_count += 1
        else:
            # Caso não tenha inciso
            final_chunks.append({
                'id': chunk_id_count,
                'source': primary_title,
                'text': (primary_title + " " + primary_content).strip()
            })
            chunk_id_count += 1

    logging.info(f"Processo concluído. Total de chunks granulares gerados: {len(final_chunks)}")

    # --- SALVA TEXTO PROCESSADO ---
    os.makedirs(os.path.dirname(PROCESSED_DATA_PATH), exist_ok=True)
    with open(PROCESSED_DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(final_chunks, f, ensure_ascii=False, indent=4)
    
    logging.info(f"Chunks salvos com sucesso em: {PROCESSED_DATA_PATH}")

if __name__ == '__main__':
    process_and_chunk()
