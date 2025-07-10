from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import json
import os
import logging

# Configuração inicial de logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')

def create_and_save_vector_db():
    """
    Carrega os chunks de texto processados, gera embeddings para cada um
    e os salva em um índice FAISS e em um arquivo de dados mapeado.
    """

    # --- CARREGA DADOS PROCESSADOS ---
    PROCESSED_DATA_PATH = os.path.join("..", "data", "processed", "lgpd_chunks.json")
    
    logging.info(f"Carregando chunks de '{PROCESSED_DATA_PATH}'...")
    try:
        with open(PROCESSED_DATA_PATH, 'r', encoding='utf-8') as f:
            chunks_data = json.load(f)
        logging.info("Chunks carregados com sucesso!")
    except FileNotFoundError:
        logging.error("Arquivos de chunks não encontrado. Execute o script de processamento de texto primeiro.")
        return

    texts = [chunk['text'] for chunk in chunks_data]
    logging.info(f"Quantidade de chunks de texto para processar: {len(texts)}")

    # --- CARREGA MODELO DE EMBEDDINGS ---
    logging.info("Carregando o modelo SentenceTransformer...")
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    # --- GERAR EMBEDDINGS ---
    logging.info("Gerando embeddings para os chunks de texto... (Isso pode levar alguns minutos)")
    embeddings = model.encode(texts, show_progress_bar=True)

    embeddings = np.array(embeddings).astype('float32')
    logging.info(f"Embeddings gerados. Formato do vetor: {embeddings.shape}")

    # --- ÍNDICE FAISS ---
    d = embeddings.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(embeddings)
    logging.info(f"Índice FAISS criado. Total de vetores no índice: {index.ntotal}")

    # --- SALVAR O ÍNDICE E OS DADOS ---
    FAISS_INDEX_PATH = os.path.join("..", "data", "processed", "lgpd_faiss.index")
    os.makedirs(os.path.dirname(FAISS_INDEX_PATH), exist_ok=True)
    
    faiss.write_index(index, FAISS_INDEX_PATH)
    logging.info(f"Índice FAISS salvo em: '{FAISS_INDEX_PATH}'")
    
    with open(PROCESSED_DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(chunks_data, f, ensure_ascii=False, indent=4)
    logging.info(f"Dados dos chunks atualizados e salvos em: '{PROCESSED_DATA_PATH}'")


if __name__ == '__main__':
    create_and_save_vector_db()