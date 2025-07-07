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

    logging.info(f"Buscando dados de: {URL}")

    try:
        logging.info("Fazendo requisição para a página...")