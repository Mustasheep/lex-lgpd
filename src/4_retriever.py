import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import logging

MODELO = 'rufimelo/bert-large-portuguese-cased-sts'

# Configuração do logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S')

class Retriever:
    """
    Encapsula a lógica para carregar o modelo, o índice FAISS e os dados,
    afim de realizar buscas de similaidade.
    """
    def __init__(self):
        # --- Estabelecendo caminhos ---
        self.base_path = os.path.join("..", "data", "processed")
        self.index_path = os.path.join(self.base_path, "lgpd_faiss.index")
        self.data_path = os.path.join(self.base_path, "lgpd_chunks.json")
        self.model_name = MODELO

        # --- Carregar todos os componentes ---
        logging.info("Inicializando o Retriever...")
        self.model = self._load_model()
        self.index = self._load_faiss_index()
        self.chunks_data = self._load_chunk_data()
        logging.info("Retriever inicializado com sucesso.")
    
    def _load_model(self):
        """
        Carrega o modelo de embeddings.
        """
        logging.info(f"Carregando modelo de embeddings: {self.model_name}")
        return SentenceTransformer(self.model_name)
    
    def _load_faiss_index(self):
        """
        Carrega o index Faiss já registrado no disco
        """
        logging.info(f"Carregando índice FAISS de: {self.index_path}")
        if not os.path.exists(self.index_path):
            logging.error("Arquivo de índice FAISS não encontrado!")
            raise FileNotFoundError("Execute o script '3_build_vector_db.py' primeiro.")
        return faiss.read_index(self.index_path)

    def _load_chunk_data(self):
        """
        Carrega os chunks, que formam o mapa de IDs para os textos
        """
        logging.info(f"Carregando dados de chunks em: {self.data_path}")
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error("Arquivo de chunks não encontrado!")
            raise FileNotFoundError("Verifique se o processamento foi concluído.")
        
    def search(self, query: str, k: int = 5):
        """
        Recebe uma query de texto, a convertendo em um embedding e busca os k chunks
        mais similares no índice FAISS.

        :param query: A pergunta do usuário
        :param k: O número de resultados a serem retornados
        :return: Uma lista de dicionários, apresentando chunks relevantes
        """
        logging.info(f"Recebida nova busca. Query: '{query}', Quantidade de Respostas: '{k}'")

        # Aplicando embeddings à query, convertendo para float e efetuando a busca
        query_embeddings = self.model.encode([query])
        query_embeddings = np.array(query_embeddings).astype('float32')
        distances, indices = self.index.search(query_embeddings, k)
        logging.info(f"Busca no FAISS concluída. Índices encontrados: {indices[0]}")

        # Mapear os IDs ao mapa de chunks
        results = [self.chunks_data[i] for i in indices[0]]

        return results
    
# --- EXECUÇÃO DO SCRIPT ---
if __name__ == '__main__':
    retriever = Retriever()

    query_teste = "O que são dados pessoais sensíveis?"
    top_results = retriever.search(query_teste, k=3)

    print("\n----- RESULTADOS DA BUSCA -----")
    print(f"Query: {query_teste}\n")
    for i, result in enumerate(top_results):
        print(f"Resultado {i+1} (ID: {result['id']}, Fonte: {result['source']}):")
        print(f"➥ {result['text']}")
        print("-" * 20)
