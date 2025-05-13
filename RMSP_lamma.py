import pandas as pd
import streamlit as st
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
import numpy as np

# Definir a URL da logo do LAMMA e imagem do cabeçalho
LOGO_LAMMA_URL_HEADER = "https://lamma.com.br/wp-content/uploads/2024/08/lammapy-removebg-preview.png"
LOGO_HEADER_PDF = "https://lamma.com.br/wp-content/uploads/2024/10/d9b5350c-12ed-4e47-a111-f37c1f97c6cf-1-1024x235.jpeg"

# Função para calcular a resistência à penetração (RSMP)
def calcular_rp(impactos):
    try:
        return (5.6 + (6.89 * impactos)) / 10.2
    except ValueError:
        return None

# Função para gerar o PDF
def gerar_pdf(fig, n_pontos, max_rp, max_camada):
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)

    # Adicionar imagem no cabeçalho
    c.drawImage(LOGO_HEADER_PDF, x=A4[0] / 2 - 150, y=750, width=300, height=60)

    # Adicionar título centralizado
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(A4[0] / 2, 720, "RESISTÊNCIA MECÂNICA DO SOLO À PENETRAÇÃO (RMSP)")

    # Subtítulo
    c.setFont("Helvetica", 12)
    c.drawCentredString(A4[0] / 2, 700, "APP desenvolvido pelo LAMMA - Laboratório de Máquinas e Mecanização Agrícola da UNESP/Jaboticabal")

    # Data de exportação
    c.setFont("Helvetica", 10)
    c.drawCentredString(A4[0] / 2, 680, f"Data de Exportação: {datetime.now().strftime('%Y-%m-%d')}")

    # Quantidade de pontos amostrados
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(A4[0] / 2, 660, f"Quantidade de pontos amostrados: {n_pontos}")

    # Adicionar o maior valor destacado em vermelho
    y = 620
    c.setFillColorRGB(1, 0, 0)  # Cor vermelha
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(A4[0] / 2, y, f"Maior valor de RP médio (MPa): {max_rp:.2f} na camada {max_camada}.")
    c.setFillColorRGB(0, 0, 0)  # Voltar para a cor preta

    # Adicionar o gráfico ao PDF
    y -= 60  # Espaçamento antes do gráfico
    fig.savefig("temp_graph.png", format="png")
    c.drawImage("temp_graph.png", 50, y - 300, width=500, height=300)

    # Adicionar a forma de citação centralizada
    y -= 320
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(
        A4[0] / 2,
        y,
        "Como citar o APP: Vieira, I. C. O. V.; Silva, R. P. Lammapy: NASA POWER - Resistência Mecânica do Solo à Penetração."
    )
    y -= 15
    c.drawCentredString(
        A4[0] / 2,
        y,
        "Disponível em: https://lamma.com.br/lammapy"
    )

    c.showPage()
    c.save()
    pdf_buffer.seek(0)

    return pdf_buffer

# Sidebar com a metodologia e outras informações
st.sidebar.title("SOBRE")
st.sidebar.subheader("Sistema de Avaliação de Resistência Mecânica do Solo à Penetração (RMSP)")
st.sidebar.write("""
Este aplicativo foi desenvolvido para auxiliar na avaliação da resistência à penetração em diferentes profundidades do solo, 
ajudando a identificar a compactação do solo e fornecer recomendações de manejo.
""")
st.sidebar.write("""
**RESPONSÁVEIS:**  
- Prof. Dr. Rouverson Pereira da Silva – FCAV/UNESP [Linkedin](https://www.linkedin.com/in/rouverson-pereira-da-silva/)
- Msc. Igor Cristian de Oliveira Vieira - FCAV/UNESP [Linkedin](https://www.linkedin.com/in/eng-igor-vieira/)
- Msc. Breno dos Santos Silva - FCAV/UNESP [Linkedin](https://www.linkedin.com/in/breno-santos-a47606250/)
""")

st.sidebar.subheader("REALIZAÇÃO")
st.sidebar.image("http://lamma.com.br/wp-content/uploads/2024/02/IMG_1713-300x81.png")
st.sidebar.write("[Visite o site do LAMMA](https://lamma.com.br/)")
st.sidebar.write("[Visite o instagram do LAMMA](https://www.instagram.com/lamma.unesp/)")
st.sidebar.write("[Visite o site do RSRG](https://www.rsrg.net.br/)")

st.sidebar.subheader("Metodologia")
st.sidebar.write("""
Para a avaliação da resistência à penetração (RP) foi utilizado um penetrômetro de impacto modelo PLANALSUCAR-STOLF de ponta fina (30°) (STOLF, 2014), cujo funcionamento consiste na penetração de uma haste com ponteira cônica, através do acionamento manual de um êmbolo de massa conhecida a uma altura constante. 
O número de impactos para romper as camadas de 0-10, 10-20, e assim sucessivamente é quantificado e aplicado na equação 1.

(1) RP (MPa) = (5.6 + (6.89 * I)) / 10.2

Em que:
- RP – resistência à penetração;
- I – número de impactos.
""")
st.sidebar.image("https://www.researchgate.net/profile/Carlos-Alberto-Campos/publication/280086942/figure/fig1/AS:669550257389584@1536644629739/Figura-03-Esquema-Penetrometro-de-Impacto_W640.jpg", caption="Penetrômetro de Impacto", use_container_width=True)

# Interface principal
st.title("Sistema de Avaliação de Resistência Mecânica do Solo à Penetração (RMSP)")
st.image(LOGO_LAMMA_URL_HEADER, use_container_width=True)
st.markdown("**APP DESENVOLVIDO PELO LAMMA - LABORATÓRIO DE MÁQUINAS E MECANIZAÇÃO AGRÍCOLA DA  UNESP/JABOTICABAL**")
st.subheader("Parâmetros de Entrada")

# Selecionar quantidade de pontos de amostragem
n_pontos = st.number_input("Selecione a quantidade de pontos de amostragem (máximo 10):", min_value=1, max_value=10, value=1)

# Camadas de 10 em 10 cm até 50 cm
camadas = ['0-10', '10-20', '20-30', '30-40', '40-50']

# Coletar dados de impactos para cada ponto de amostragem
dados_pontos = []
for i in range(1, n_pontos + 1):
    st.header(f"Ponto de Amostragem {i}")
    impactos = {camada: st.number_input(f"Impactos no Ponto {i} - Camada {camada} cm", min_value=0, value=0, step=1) for camada in camadas}
    dados_pontos.append(impactos)

if st.button("Gerar Gráfico e Relatório"):
    # Calcular RP para cada ponto e cada camada
    resultados = []
    for i, impactos in enumerate(dados_pontos):
        for camada in camadas:
            rp = calcular_rp(impactos[camada])
            resultados.append({"Ponto": i + 1, "Camada (cm)": camada, "RP (MPa)": rp})

    df_resultados = pd.DataFrame(resultados)

    # Calcular médias de RP por camada
    media_rp = df_resultados.groupby("Camada (cm)")["RP (MPa)"].mean().reset_index()
    media_rp.rename(columns={"RP (MPa)": "RP Médio (MPa)"}, inplace=True)

    # Identificar o maior valor de RP médio e a camada correspondente
    max_rp = media_rp['RP Médio (MPa)'].max()
    max_camada = media_rp.loc[media_rp['RP Médio (MPa)'].idxmax(), 'Camada (cm)']

    # Gráfico de médias de RP sem divisões de classe
    rp_values = np.array(media_rp['RP Médio (MPa)'])
    profundidades = np.array([int(camada.split('-')[0]) for camada in media_rp['Camada (cm)']])

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(rp_values, profundidades, 'o-', label='Média de Resistência à Penetração', markersize=5, linewidth=2)
    ax.axvline(x=max_rp, color='red', linestyle='--', label=f'Maior RP ({max_rp:.2f} MPa) - Camada {max_camada}')
    ax.set_xlabel('Resistência à Penetração (MPa)')
    ax.set_ylabel('Profundidade (cm)')
    ax.set_title('Média de Resistência Mecânica do Solo à Penetração')
    ax.legend()
    ax.invert_yaxis()
    st.pyplot(fig)

    # Mostrar informações sobre o maior valor na interface
    st.markdown(f"<span style='color:red;'>**Maior valor de RP médio (MPa): {max_rp:.2f} na camada {max_camada}.**</span>", unsafe_allow_html=True)
    st.markdown(f"**Quantidade de pontos amostrados:** {n_pontos}.")

    # Gerar PDF com os resultados
    pdf_output = gerar_pdf(fig, n_pontos, max_rp, max_camada)

    # Botão para download do PDF
    st.download_button(label="Baixar Relatório em PDF", data=pdf_output, file_name="relatorio_resistencia_penetracao.pdf", mime="application/pdf")

    # Adicionar botão para download do gráfico
    fig.savefig("grafico_resistencia_penetracao.png", format="png")
    with open("grafico_resistencia_penetracao.png", "rb") as file:
        st.download_button(
            label="Download do Gráfico",
            data=file,
            file_name="grafico_resistencia_penetracao.png",
            mime="image/png"
        )

    # Forma de citação
    st.markdown("""
    **Como citar este APP:**  
    Vieira, I. C. O. V.; Silva, R. P. Lammapy: NASA POWER - Resistência Mecânica do Solo à Penetração.  
    Disponível em: [https://lamma.com.br/lammapy](https://lamma.com.br/lammapy)
    """)


 #streamlit run "c:/Users/Igor Vieira/App_Lamma/RMSP_lamma.py"

