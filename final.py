import pandas as pd
import time
import re
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def adicionar_espacos(texto, lista_palavras):
    for palavra in lista_palavras:
        padrao = re.compile(rf'\b{re.escape(palavra)}\b')
        texto = re.sub(padrao, f' {palavra}', texto)
    return texto

contador = 0
services = webdriver.ChromeService()
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=services, options=options)
url = 'https://transparencia.ac.gov.br/#/servidor-publico'
driver.get(url)
time.sleep(5)
#seletores das combobox
combobox_situacao = driver.find_elements(by=By.CLASS_NAME, value="conteudo-bloco-filtro-select")[0]
select = Select(combobox_situacao)
select.select_by_visible_text("Todos")

combobox_periodo_mes = driver.find_elements(by=By.CLASS_NAME, value="conteudo-bloco-filtro-select")[1]
select = Select(combobox_periodo_mes)
select.select_by_visible_text("Janeiro")

combobox_periodo_ano = driver.find_elements(by=By.CLASS_NAME, value="conteudo-bloco-filtro-select")[2]
select = Select(combobox_periodo_ano)
select.select_by_value("2023")

#click no botão FILTRAR
driver.find_element(by=By.TAG_NAME, value="button").click()

#esperando a página responder
#time.sleep(50)

wait = WebDriverWait(driver, 90)
wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

#pegando a tabela e as linhas
# Loop principal

registros = []
while contador < 10:
    # Seletor para o botão "Próximo page"
    proximo_page_selector = "//a[@aria-label='Próximo page']"

    # Esperar até que o botão "Próximo page" esteja disponível
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, proximo_page_selector)))

    # Pegar a tabela e as linhas
    tabela = driver.find_element(By.XPATH, "//table")
    colunas = tabela.find_elements(By.XPATH, "//thead/tr/th")
    linhas = tabela.find_elements(By.XPATH, "//tbody/tr")

    nomes_colunas = [header.text for header in colunas]
    dados_linhas = [i.text for i in linhas]

    grupos_palavras = ['APOSENTADO', 'EM EXERCÍCIO', 'EM FÉRIAS', 'PENSIONISTA', 'AFASTADO/LICENCIADO']

    caminho_arquivo = 'cargos_servidor.csv'

    df = pd.read_csv(caminho_arquivo, header=None, names=['Cargos'], quoting=3)

    # Extrair a coluna 'Cargos' como uma lista
    lista_cargos = df['Cargos'].tolist()

    # Criar uma lista de dicionários
  

    for linha in dados_linhas:
        linha = adicionar_espacos(linha, grupos_palavras)
        linha = adicionar_espacos(linha, lista_cargos)
        # Dividir a linha em partes usando o método split
        partes = linha.split("  ")

        # Criar um dicionário vazio para armazenar os dados desta linha
        registro = {}

        # Iterar sobre as colunas e adicionar os valores correspondentes
        for i in range(len(nomes_colunas)):
            coluna = nomes_colunas[i]
            valor = partes[i] if i < len(partes) else ""  # Tratar o caso em que a linha não tem todas as colunas
            registro[coluna] = valor

        # Adicionar o dicionário à lista de registros
        registros.append(registro)

    time.sleep(5)
    # Clicando para a próxima
    driver.find_element(By.XPATH, proximo_page_selector).click()

    time.sleep(10)
    contador += 1


# Exibir os registros
#for registro in registros:
#   print(registro)

df = pd.DataFrame(registros)
print(df)
df.to_csv('acre_boladao.csv')
