import pandas as pd
import streamlit as st
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
import numpy as np

# Definir a URL da logo do LAMMA
LOGO_LAMMA_URL_HEADER = "https://lamma.com.br/wp-content/uploads/2024/08/lammapy-removebg-preview.png"
LOGO_LAMMA_URL_PDF = "https://lamma.com.br/wp-content/uploads/2024/02/LAMMA-1024-x-512-px-197x25.png"

# Função para calcular a resistência à penetração (RSMP)
def calcular_rp(impactos):
    try:
        return (5.6 + (6.89 * impactos)) / 10.2
    except ValueError:
        return None

# Função para calcular a redução percentual
def calcular_reducao(rp_antes, rp_depois):
    if rp_antes > 0:
        return 100 * (rp_antes - rp_depois) / rp_antes
    return 0

# Sidebar com a metodologia e outras informações
st.sidebar.title("SOBRE")
st.sidebar.subheader("Sistema de Avaliação de Resistência Mecânica do Solo à Penetração (RMSP)")
st.sidebar.write("""
Este aplicativo foi desenvolvido para auxiliar na avaliação da resistência à penetração em diferentes profundidades do solo, 
ajudando a identificar a compactação do solo e fornecer recomendações de manejo.
""")
st.sidebar.write("""
*RESPONSÁVEIS:*  
- Prof. Dr. Rouverson Pereira da Silva – FCAV/UNESP [Linkedin](https://www.linkedin.com/in/rouverson-pereira-da-silva/)
- Msc. Igor Cristian de Oliveira Vieira - FCAV/UNESP [Linkedin](https://www.linkedin.com/in/eng-igor-vieira/)
""")

# Sidebar "REALIZAÇÃO"
st.sidebar.subheader("REALIZAÇÃO")
st.sidebar.image("http://lamma.com.br/wp-content/uploads/2024/02/IMG_1713-300x81.png")
st.sidebar.write("[Visite o site do LAMMA](https://lamma.com.br/)")
st.sidebar.write("[Visite o instagram do LAMMA](https://www.instagram.com/lamma.unesp/)")
st.sidebar.write("[Visite o site do RSRG](https://www.rsrg.net.br/)")

# Sidebar com a metodologia
st.sidebar.subheader("Metodologia")
st.sidebar.write("""
Para a avaliação da resistência à penetração (RP) foi utilizado um penetrômetro de impacto modelo PLANALSUCAR-STOLF de ponta fina (30°) (STOLF, 2014), cujo funcionamento consiste na penetração de uma haste com ponteira cônica, através do acionamento manual de um êmbolo de massa conhecida a uma altura constante. 
O número de impactos para romper as camadas de 0-5, 5-10, e assim sucessivamente é quantificado e aplicado na equação 1.

(1) RP (MPa) = (5.6 + (6.89 * I)) / 10.2

Em que:
- RP – resistência à penetração;
- I – número de impactos.
""")

# Adicionar imagem do penetrômetro de impacto
st.sidebar.image("https://www.researchgate.net/profile/Carlos-Alberto-Campos/publication/280086942/figure/fig1/AS:669550257389584@1536644629739/Figura-03-Esquema-Penetrometro-de-Impacto_W640.jpg", caption="Penetrômetro de Impacto", use_column_width=True)

# Função para gerar as dicas de subsolagem
def dicas_para_subsolagem ():
    return """

1. Escolha uma profundidade 5 cm abaixo da camada compactada.
Use a fórmula: P = (5 a 7) x largura da ponteira (b).
Exemplo: Se a largura da ponteira for 7 cm, a profundidade deve ser entre 35 e 49 cm.
2. Ajuste o espaçamento entre as hastes com base na potência do trator e no tipo de ponteira:
Ponteiras sem asas: Espaçamento entre 1,0 e 1,5 vezes a profundidade (P).
Ponteiras com asas: Espaçamento entre 1,5 e 2,0 vezes a profundidade (P).
Exemplo: Para uma profundidade de 40 cm, o espaçamento seria de 40 a 60 cm (sem asas) e de 60 a 80 cm (com asas).
3. Trabalhe com uma velocidade de operação entre 4 e 6 km/h para garantir eficiência no rompimento do solo.
4. Realize a subsolagem com o solo levemente úmido para facilitar o rompimento da camada compactada e evitar danos.

    """

# Função para gerar o PDF
def gerar_pdf(resultados, media_rp_antes, media_rp_depois, dicas, fig):
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)

    # Adicionar título
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(A4[0] / 2, 780, "RESISTÊNCIA MECÂNICA DO SOLO À PENETRAÇÃO (RMSP)")

    # Adicionar subtítulo
    c.setFont("Helvetica", 12)
    c.drawCentredString(A4[0] / 2, 760, "APP desenvolvido pelo LAMMA - Laboratório de Máquinas e Mecanização Agrícola da UNESP/ Jaboticabal")

    # Subtítulo do relatório
    c.drawCentredString(A4[0] / 2, 740, "Relatório de compactação do solo antes e depois da subsolagem")
    
    # Data de exportação
    c.drawString(50, 720, f"Data de Exportação: {datetime.now().strftime('%Y-%m-%d')}")

    # Exibir valor médio de RP
    c.setFont("Helvetica-Bold", 12)
    c.setFillColorRGB(1, 0, 0)  # Cor vermelha
    c.drawString(50, 690, f"RP Médio Antes (MPa): {media_rp_antes:.2f}")
    c.drawString(50, 670, f"RP Médio Depois (MPa): {media_rp_depois:.2f}")
    c.setFillColorRGB(0, 0, 0)  # Voltar para a cor preta

    # Tabela de Resultados
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 640, "Resultados")

    # Cabeçalho da tabela
    c.setFont("Helvetica", 10)
    y = 620
    c.drawString(50, y, "Camada (cm)")
    c.drawString(150, y, "RP Médio Antes (MPa)")
    c.drawString(300, y, "RP Médio Depois (MPa)")
    c.drawString(450, y, "Redução (%)")

    # Iterar sobre os resultados e adicioná-los à tabela
    for index, row in resultados.iterrows():
        y -= 20
        c.drawString(50, y, row['Camada (cm)'])
        c.drawString(150, y, f"{row['RP Médio Antes (MPa)']:.2f}")
        c.drawString(300, y, f"{row['RP Médio Depois (MPa)']:.2f}")
        c.drawString(450, y, f"{row['Redução %']:.2f}")

    # Adicionar o gráfico ao PDF
    y -= 40  # Espaçamento antes do gráfico
    fig.savefig("temp_graph.png", format="png")
    c.drawImage("temp_graph.png", 50, y - 200, width=500, height=200)

    # Adicionar as dicas ao PDF
    y -= 220
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Dicas para Subsolagem")

    y -= 20
    c.setFont("Helvetica", 10)
    for linha in dicas.split("\n"):
        if linha.strip():
            c.drawString(50, y, linha.strip())
            y -= 15

    c.showPage()
    c.save()
    pdf_buffer.seek(0)

    return pdf_buffer

# Interface principal
st.title("Resistência Mecânica do Solo à Penetração (RMSP)")
st.image(LOGO_LAMMA_URL_HEADER, use_column_width=True)
st.markdown("*APP desenvolvido pelo LAMMA - Laboratório de Máquinas e Mecanização Agrícola da UNESP/Jaboticabal*")
st.subheader("Parâmetros de Entrada")

# Camadas de 5 em 5 cm até 50 cm
camadas = ['0-5', '5-10', '10-15', '15-20', '20-25', '25-30', '30-35', '35-40', '40-45', '45-50']

with st.form("input_form"):
    st.header("Dados Antes da Subsolagem")
    impactos_antes = {camada: st.number_input(f"Impactos Antes {camada} cm", min_value=0, value=0, step=1) for camada in camadas}
    
    st.header("Dados Depois da Subsolagem")
    impactos_depois = {camada: st.number_input(f"Impactos Depois {camada} cm", min_value=0, value=0, step=1) for camada in camadas}

    submitted = st.form_submit_button("Calcular")

if submitted:
    resultados = []
    erro_encontrado = False
    for camada in camadas:
        rp_antes = calcular_rp(impactos_antes[camada])
        rp_depois = calcular_rp(impactos_depois[camada])
        reducao_percentual = calcular_reducao(rp_antes, rp_depois)

        if rp_antes is None or rp_depois is None:
            st.error(f"Erro: Entrada inválida na camada {camada}. Insira valores numéricos válidos.")
            erro_encontrado = True
            break

        resultados.append({
            "Camada (cm)": camada,
            "RP Médio Antes (MPa)": rp_antes,
            "RP Médio Depois (MPa)": rp_depois,
            "Redução %": reducao_percentual
        })

    if not erro_encontrado:
        df_resultados = pd.DataFrame(resultados)
        st.table(df_resultados)

        # Gráfico de comparação
        rp_antes = np.array(df_resultados['RP Médio Antes (MPa)'])
        rp_depois = np.array(df_resultados['RP Médio Depois (MPa)'])
        profundidades = np.array([int(camada.split('-')[0]) for camada in camadas])

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(rp_antes, profundidades, 'o-', label='RP Antes', marker='o', markersize=5, linewidth=2)
        ax.plot(rp_depois, profundidades, 'o-', label='RP Depois', marker='o', markersize=5, linewidth=2)
        ax.set_xlabel('Resistência à Penetração (MPa)')
        ax.set_ylabel('Profundidade (cm)')
        ax.set_title('Comparação de Resistência à Penetração por Profundidade')
        ax.legend()
        ax.invert_yaxis()
        st.pyplot(fig)

        # Calcular valores médios
        media_rp_antes = rp_antes.mean()
        media_rp_depois = rp_depois.mean()

        # Gerar PDF com resultados, gráfico e dicas
        dicas = dicas_para_subsolagem()
        pdf_output = gerar_pdf(df_resultados, media_rp_antes, media_rp_depois, dicas, fig)

        # Botão para download do PDF
        st.download_button(label="Baixar Relatório em PDF", data=pdf_output, file_name="relatorio_resistencia_penetracao.pdf", mime="application/pdf")

        
 #streamlit run "c:/Users/Igor Vieira/App_Lamma/RMSP_lamma.py"

        
 #streamlit run "c:/Users/Igor Vieira/App_Lamma/RMSP_lamma.py"

