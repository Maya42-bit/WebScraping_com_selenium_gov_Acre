import pandas as pd
import time
import re
import csv
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
time.sleep(7)
#seletores das combobox
combobox_situacao = driver.find_elements(by=By.CLASS_NAME, value="conteudo-bloco-filtro-select")[0]
select = Select(combobox_situacao)
select.select_by_visible_text("Todos")                                                                                              #<========= COLOCAR OS SERVIDORES AQUI

combobox_periodo_mes = driver.find_elements(by=By.CLASS_NAME, value="conteudo-bloco-filtro-select")[1]
select = Select(combobox_periodo_mes)
select.select_by_visible_text("Fevereiro")                                                                                          #<========= COLCOAR O MÊS A SER BUSCADO AQUI

combobox_periodo_ano = driver.find_elements(by=By.CLASS_NAME, value="conteudo-bloco-filtro-select")[2]
select = Select(combobox_periodo_ano)
select.select_by_value("2023")                                                                                                      #<========= COLOCAR O ANO A SER BUSCADO AQUI
time.sleep(1)
#click no botão FILTRAR
driver.find_element(by=By.TAG_NAME, value="button").click()

#esperando a página responder
#time.sleep(50)

wait = WebDriverWait(driver, 90)
wait.until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))

#pegando a tabela e as linhas
# Loop principal

registros = []
while contador < 5276:
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

    grupos_palavras = ['APOSENTADO', 'EM EXERCÍCIO', 'EM FÉRIAS', 'PENSIONISTA', 'AFASTADO/LICENCIADO', 'EXONERADO/RESCISO', 'CEDIDO']

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

    time.sleep(3)
          #adicionar em arquivo csv
    contador += 1
    with open("Bases/acre_boladao_FEV_2023.csv", "a", encoding="utf8") as f:                                                            #<====== COLOCAR O NOME DO ARQUIVO AQUI
        csv_writer = csv.writer(f)
        if contador ==1: csv_writer.writerow(nomes_colunas) 

        for registro in registros:
            linha_csv = [registro[coluna] for coluna in nomes_colunas]
            csv_writer.writerow(linha_csv)
    
    # Clicando para a próxima
    driver.find_element(By.XPATH, proximo_page_selector).click()
   
    registros = []


# Exibir os registros
#for registro in registros:
#   print(registro)
'''
df = pd.DataFrame(registros)
print(df)
df.to_csv('acre_boladao.csv', index=False)
'''