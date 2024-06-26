import time
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import schedule
import telebot
import pytz
import pandas as pd

linha = 11

# ---------------------------------------------------------------------------------------------------------------------
# INÍCIO DAS PRÉ-DEFINIÇÕES

@st.cache_resource
def pre_definicoes():

    # Define o intervalo de tempo desejado em segundos
    # intervalo_tempo = 70
    intervalo_tempo = 360
    referencia_consumo = 1350

    # Configurações de autenticação do bot Telegram
    chave = st.secrets["lista_chave"]['list_key']
    bot_token = chave[0]
    chat_id = [chave[1], chave[2]]

    # Cria uma instância do bot Telegram
    bot = telebot.TeleBot(bot_token)

    # credenciais do serviço
    SCOPE = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = st.secrets["gcp_service_account_3"]

    # autenticação do serviço
    creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_FILE, scopes=SCOPE, )
    client = gspread.authorize(creds)

    # identificador das planilhas
    planilha = st.secrets['lista_id_planilha']['id_planilha']
    SOURCE_SPREADSHEET_ID = planilha[0]
    TARGET_SPREADSHEET_ID = planilha[1]

    # Fuso horário brasileiro
    tz = pytz.timezone('America/Sao_Paulo')
    return intervalo_tempo, referencia_consumo, chat_id, bot, client, SOURCE_SPREADSHEET_ID, TARGET_SPREADSHEET_ID, tz

intervalo_tempo, referencia_consumo, chat_id, bot, client, SOURCE_SPREADSHEET_ID, TARGET_SPREADSHEET_ID, tz = pre_definicoes()

# TÉRMINO DAS PRÉ-DEFINIÇÕES
# ---------------------------------------------------------------------------------------------------------------------

#@st.cache_resource
#def acessar_planilha_log_de_conexao():
#    return pd.DataFrame(client.open_by_key(TARGET_SPREADSHEET_ID).sheet1.get_all_records())

#@st.cache_resource
#def acessar_planilha_dados_climatizacao():
#    return pd.DataFrame(client.open_by_key(SOURCE_SPREADSHEET_ID).sheet1.get_all_records())


linha = 63


def debugging_codigo(horario_atual, horario_ultima_linha_rpi, horario_ultima_linha_pc_debugging, consumo_ultima_linha,
                     rpi_on, pc_on, consumo_alto, condicao_1, condicao_2, condicao_3):
    print(f''' \n
            hora atual: {horario_atual} \n
            hora rpi: {horario_ultima_linha_rpi} \n
            hora pc: {horario_ultima_linha_pc_debugging} \n
            consumo: {consumo_ultima_linha} \n \n
            horario atual: {datetime.strptime(horario_atual, '%Y-%m-%d %H:%M:%S').timestamp()} : {datetime.now()} \n
            ultimo horario rpi: {horario_ultima_linha_rpi.timestamp()} \n
            ultimo horario pc: {horario_ultima_linha_pc_debugging} \n \n
            rpi_on: {rpi_on} \n
            pc_on: {pc_on} \n
            consumo_alto: {consumo_alto} \n \n
            Condição 1: {condicao_1} \n
            Condição 2: {condicao_2} \n
            Condição 3: {condicao_3} \n
            -----------------------------------------------------------------------------''')


def enviar_mensagem_admin(mensagem):
    bot.send_message(chat_id=chat_id[0], text=mensagem, timeout=150)


def enviar_mensagem_grupo(mensagem):
    bot.send_message(chat_id=chat_id[1], text=mensagem, timeout=150)


# Função que verifica se já passou o intervalo de tempo definido e se houve novas linhas adicionadas na planilha
def verifica_planilha():
    global texto_admin, texto_grupo, garantir_execucao_unica
    time.sleep(15)
    if garantir_execucao_unica:
        try:

            linha = 85

            target_sheet = pd.DataFrame(client.open_by_key(TARGET_SPREADSHEET_ID).sheet1.get_all_records())
            try: #Remover depois
                source_sheet = d.DataFrame(client.open_by_key(SOURCE_SPREADSHEET_ID).sheet1.get_all_records())
            except: #Remover depois
                pass

            linha = 93

            horario_atual = datetime.strftime(datetime.now().replace(tzinfo=pytz.utc).astimezone(tz),
                                              '%Y-%m-%d %H:%M:%S')
            horario_ultima_linha_rpi = pd.to_datetime(target_sheet['DATA-RPI']).dropna().tail(1).reset_index(drop=True)[
                0]
            horario_primeira_linha_rpi = \
            pd.to_datetime(target_sheet['DATA-RPI']).dropna().head(1).reset_index(drop=True)[0]

            linha = 102

            try:

                linha = 106

                horario_ultima_linha_pc = \
                    pd.to_datetime(target_sheet['DATA-PC']).dropna().tail(1).reset_index(drop=True)[0]
                horario_primeira_linha_pc = \
                    pd.to_datetime(target_sheet['DATA-PC']).dropna().head(1).reset_index(drop=True)[0]
                horario_ultima_linha_pc_debugging = horario_ultima_linha_pc.timestamp()
            except:

                linha = 115

                horario_ultima_linha_pc_debugging = 'PC Desligado!'

            linha = 119

            try: #Remover depois
                consumo_ultima_linha = \
                source_sheet[['Potência Ativa A', 'Potência Ativa B', 'Potência Ativa C']].tail(1).reset_index(
                    drop=True).sum(axis=1)[0]
                hora_ultimo_consumo = pd.to_datetime(source_sheet['Hora']).dropna().tail(1).reset_index(drop=True)
            except: #Remover depois
                pass

                if horario_ultima_linha_pc_debugging == 'PC Desligado!':
                    rpi_on = datetime.strptime(horario_atual,
                                               '%Y-%m-%d %H:%M:%S').timestamp() - horario_ultima_linha_rpi.timestamp() <= 300
                else:
                    rpi_on = datetime.strptime(horario_atual,
                                               '%Y-%m-%d %H:%M:%S').timestamp() - horario_ultima_linha_rpi.timestamp() <= intervalo_tempo
                try: #Remover depois
                    linha = 136

                    pc_on = datetime.strptime(horario_atual,
                                              '%Y-%m-%d %H:%M:%S').timestamp() - horario_ultima_linha_pc.timestamp() <= intervalo_tempo
                    consumo_alto = consumo_ultima_linha > referencia_consumo
                except: #Remover depois
                    pass

                linha = 144

                pc_on = False
                consumo_alto = False

                linha = 149

                try: #Remover depois
                    condicao_1 = not rpi_on and not pc_on and consumo_alto
                    condicao_2 = not pc_on and (rpi_on or consumo_alto)
                    condicao_3 = rpi_on or pc_on or consumo_alto

                    # Para debbuging do código
                    debugging_codigo(horario_atual, horario_ultima_linha_rpi, horario_ultima_linha_pc_debugging,
                                     consumo_ultima_linha,
                                     rpi_on, pc_on, consumo_alto, condicao_1, condicao_2, condicao_3)
                except: #Remover depois
                    pass

            if horario_ultima_linha_pc_debugging == 'PC Desligado!':
                if rpi_on:
                    if texto_admin != 'teste SOMENTE O RASPBERRY PI ESTÁ CONECTADO COM A INTERNET, RELIGUE O COMPUTADOR!':
                        texto_admin = 'teste SOMENTE O RASPBERRY PI ESTÁ CONECTADO COM A INTERNET, RELIGUE O COMPUTADOR!'
                        texto_grupo = f'teste O GEDAE ESTÁ ABERTO! \nAbriu às {horario_primeira_linha_rpi.time()} do dia {horario_primeira_linha_rpi.strftime("%d/%m/%Y")}.'
                        enviar_mensagem_grupo(texto_grupo)
                    enviar_mensagem_admin(texto_admin)
                else:
                    if texto_admin != 'teste PERDA DE CONEXÃO COM A INTERNET E BAIXO CONSUMO DE ENERGIA!':
                        texto_admin = 'teste PERDA DE CONEXÃO COM A INTERNET E BAIXO CONSUMO DE ENERGIA!'
                        texto_grupo = f'teste O GEDAE ESTÁ FECHADO! \nFechou às {horario_ultima_linha_rpi.time()} do dia {horario_ultima_linha_rpi.strftime("%d/%m/%Y")}.'
                        enviar_mensagem_grupo(texto_grupo)
                    enviar_mensagem_admin(texto_admin)
            else:

                linha = 178

                try: #Remover depois
                    Forçar_erro = source_sheet
                    energia = 0
                    if condicao_1:
                        energia = 1
                        # print('O GEDAE ESTÁ SEM ENERGIA!')
                    elif condicao_2:
                        energia = 2
                        # print('HOUVE QUEDA DE ENERGIA NO GEDAE, RELIGUE O COMPUTADOR!')
                    else:
                        # print('O GEDAE ESTÁ FUNCIONANDO NORMALMENTE!')
                        pass

                    linha = 193

                    aberto = 1
                    if condicao_3:
                        # print('O GEDAE ESTÁ ABERTO!')
                        pass
                    else:
                        aberto = 0
                        # print('O GEDAE ESTÁ FECHADO!')

                    linha = 203

                    if aberto == 1:
                        if energia == 0:
                            # print('O GEDAE ESTÁ ABERTO E TUDO ESTÁ FUNCIONANDO NORMALMENTE!')
                            if texto_admin != 'teste O COMPUTADOR ESTÁ CONECTADO COM A INTERNET!' or texto_admin == 'teste SOMENTE O RASPBERRY PI ESTÁ CONECTADO COM A INTERNET, RELIGUE O COMPUTADOR!':
                                texto_admin = 'teste O COMPUTADOR ESTÁ CONECTADO COM A INTERNET!'
                                menor_horario = min([horario_primeira_linha_rpi, horario_primeira_linha_pc])
                                texto_grupo = f'teste O GEDAE ESTÁ ABERTO! \nAbriu às {menor_horario.time()} do dia {menor_horario.strftime("%d/%m/%Y")}.'
                                enviar_mensagem_grupo(texto_grupo)
                            enviar_mensagem_admin(texto_admin)

                        elif energia == 1:
                            if hora_ultimo_consumo.dt.hour[0] < 18:
                                # print('O GEDAE ESTÁ SEM ENERGIA!')
                                if texto_admin != 'teste PERDA DE CONEXÃO COM A INTERNET E ALTO CONSUMO DE ENERGIA!':
                                    texto_admin = 'teste PERDA DE CONEXÃO COM A INTERNET E ALTO CONSUMO DE ENERGIA!'
                                    menor_horario = min([horario_primeira_linha_rpi, horario_primeira_linha_pc])
                                    texto_grupo = f'teste O GEDAE ESTÁ SEM ENERGIA!'
                                    enviar_mensagem_grupo(texto_grupo)
                                enviar_mensagem_admin(texto_admin)

                            else:
                                # print('O GEDAE ESTÁ FECHADO!')
                                if texto_admin != 'teste PERDA DE CONEXÃO COM A INTERNET E ALTO CONSUMO DE ENERGIA APÓS AS 18H00!':
                                    texto_admin = 'teste PERDA DE CONEXÃO COM A INTERNET E ALTO CONSUMO DE ENERGIA APÓS AS 18H00!'
                                    maior_horario = max([horario_ultima_linha_rpi, horario_ultima_linha_pc])
                                    texto_grupo = f'teste O GEDAE ESTÁ FECHADO! \nFechou às {maior_horario.time()} do dia {maior_horario.strftime("%d/%m/%Y")}.'
                                    enviar_mensagem_grupo(texto_grupo)
                                enviar_mensagem_admin(texto_admin)

                        elif energia == 2:
                            # print('O GEDAE ESTÁ ABERTO, MAS HOUVE QUEDA DE ENERGIA. RELIGUE O COMPUTADOR!')
                            if texto_admin != 'teste SOMENTE O RASPBERRY PI ESTÁ CONECTADO COM A INTERNET, RELIGUE O COMPUTADOR!':
                                texto_admin = 'teste SOMENTE O RASPBERRY PI ESTÁ CONECTADO COM A INTERNET, RELIGUE O COMPUTADOR!'
                                texto_grupo = f'teste ENERGIA RESTABELECIDA NO GEDAE!'
                                enviar_mensagem_grupo(texto_grupo)
                            enviar_mensagem_admin(texto_admin)

                    else:
                        # print('O GEDAE ESTÁ FECHADO!')
                        if texto_admin != 'teste PERDA DE CONEXÃO COM A INTERNET E BAIXO CONSUMO DE ENERGIA!':
                            texto_admin = 'teste PERDA DE CONEXÃO COM A INTERNET E BAIXO CONSUMO DE ENERGIA!'
                            maior_horario = max([horario_ultima_linha_rpi, horario_ultima_linha_pc])
                            texto_grupo = f'teste O GEDAE ESTÁ FECHADO! \nFechou às {maior_horario.time()} do dia {maior_horario.strftime("%d/%m/%Y")}.'
                            enviar_mensagem_grupo(texto_grupo)
                        enviar_mensagem_admin(texto_admin)

                except: #Remover depois
                    if rpi_on:
                        if texto_admin != 'teste SOMENTE O RASPBERRY PI ESTÁ CONECTADO COM A INTERNET, RELIGUE O COMPUTADOR!':
                            texto_admin = 'teste SOMENTE O RASPBERRY PI ESTÁ CONECTADO COM A INTERNET, RELIGUE O COMPUTADOR!'
                            texto_grupo = f'teste O GEDAE ESTÁ ABERTO! \nAbriu às {horario_primeira_linha_rpi.time()} do dia {horario_primeira_linha_rpi.strftime("%d/%m/%Y")}.'
                            enviar_mensagem_grupo(texto_grupo)
                        enviar_mensagem_admin(texto_admin)
                    else:
                        if texto_admin != 'teste PERDA DE CONEXÃO COM A INTERNET E BAIXO CONSUMO DE ENERGIA!':
                            texto_admin = 'teste PERDA DE CONEXÃO COM A INTERNET E BAIXO CONSUMO DE ENERGIA!'
                            texto_grupo = f'teste O GEDAE ESTÁ FECHADO! \nFechou às {horario_ultima_linha_rpi.time()} do dia {horario_ultima_linha_rpi.strftime("%d/%m/%Y")}.'
                            enviar_mensagem_grupo(texto_grupo)
                        enviar_mensagem_admin(texto_admin)

        except Exception as e:
            bot.send_message(chat_id=chat_id[0], text=f'''Erro: {str(e)}

Erro na linha: {linha}''', timeout=150)
            # time.sleep(60 - datetime.now(tz).second)
            pass
        garantir_execucao_unica = False


# if st.button("Iniciar Robô"):
if st.text_input('Senha: ') == st.secrets['senha']['senha']:
    # agenda a execução da função a cada 5 minuto
    while True:
        if datetime.now(tz).minute / 5 == int(datetime.now(tz).minute / 5) or datetime.now(tz).minute == 0:
            break
    schedule.every(5).minutes.do(verifica_planilha)

    texto_admin, texto_grupo = '', ''
    # loop principal para executar o agendador de tarefas
    while True:
        garantir_execucao_unica = True
        schedule.run_pending()
else:
    st.write('Digite a senha!')
