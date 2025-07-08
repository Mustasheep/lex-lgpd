import requests
from bs4 import BeautifulSoup
import logging
import os

# Configuração do logging
logging.basicConfig(level=logging.INFO, format= '%(asctime)s - %(levelname)s - %(message)s')

def busca_e_salva_lgpd():
    """
    Busca o conteúdo da página da LGPD no site do Planalto,
    extrai o texto principal e o salva em um arquivo .txt
    """
    URL = "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm"
    RAW_DATA_PATH = os.path.join ("..", "data", "raw", "lgpd_raw_.txt")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0',
    }

    logging.info(f"Buscando dados de: {URL}")
    try:
        logging.info("Fazendo requisição para a página...")
        response = requests.get(URL, headers=headers)
        response.raise_for_status()

        logging.info("Analisando o HTML da página...")
        soup = BeautifulSoup(response.content, 'html.parser')

        # Buscando o id dentro do div 
        texto_lei = soup.find(id='textoimpressao')

        if texto_lei:
            logging.info("Texto com as leis encontrado, extraindo o texto...")
            texto_puro = texto_lei.get_text(separator='\n', strip=True)

            # Criando os diretórios
            os.makedirs(os.path.dirname(RAW_DATA_PATH), exist_ok=True)

            with open(RAW_DATA_PATH, 'w', encoding='utf-8') as f:
                logging.info(f"O texto foi salvo com sucesso em: {RAW_DATA_PATH}")
                f.write(texto_puro)
        else:
            logging.error("Não foi possível encontrar o elemento chave para extração do texto.")
    
    except requests.exceptions.RequestException as e:
        logging.critical(f"Erro ao fazer a requisição HTTP: {e}")

if __name__ == '__main__':
    busca_e_salva_lgpd()