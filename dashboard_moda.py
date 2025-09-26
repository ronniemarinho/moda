import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from io import BytesIO
import matplotlib.pyplot as plt

# =============================
# Configuração da página
# =============================
st.set_page_config(page_title="Consumo de Moda – Dashboard", layout="wide")
st.title("📊 Consumo de Moda – Faap 2025")
st.caption("Estudo realizado pela professora Lilian Fortuna")

# =============================
# 1) Carregamento da base
# =============================
df_raw = pd.read_excel("moda.xlsx")
df = df_raw.copy()
df.columns = [c.replace("\n", " ").strip() for c in df.columns]

# =============================
# 2) Colunas principais
# =============================
COL_GENERO = "Qual é o seu gênero?"
COL_IDADE = "Qual é a sua faixa etária?"
COL_ESCOLAR = "Qual é o seu grau de escolaridade?"
COL_RENDA = "Qual é sua faixa de renda mensal?"
COL_CIDADE = "Qual a sua cidade e estado?"
COL_FREQ = "Com que frequência você compra roupas novas?"
COL_REFORMA = "Você já reformou alguma peça de roupa antiga para torná-la mais atual?"
COL_MARCA_SUST = "Você já comprou ou conhece marcas que promovem moda sustentável?"
COL_GASTO = "Quanto você gasta, em média, com roupas por mês?"
COL_2MAO = "Você compra roupas de segunda mão (ex: brechós/desapegos)?"
COL_IMPACTO = "Você acredita que o consumo de moda impacta o meio ambiente?"
COL_ODS = "Você relaciona suas escolhas de vestuário com os Objetivos de Desenvolvimento Sustentável (ODS)?"
COL_MOTIVACAO = "Qual é a sua principal motivação para suas escolhas de consumo de moda?"

# =============================
# 3) Sidebar – filtros
# =============================
st.sidebar.header("Filtros")
genero_sel = st.sidebar.multiselect("Gênero", df[COL_GENERO].dropna().unique(), default=df[COL_GENERO].dropna().unique())
idade_sel = st.sidebar.multiselect("Faixa etária", df[COL_IDADE].dropna().unique(), default=df[COL_IDADE].dropna().unique())
escolar_sel = st.sidebar.multiselect("Escolaridade", df[COL_ESCOLAR].dropna().unique(), default=df[COL_ESCOLAR].dropna().unique())
renda_sel = st.sidebar.multiselect("Faixa de renda", df[COL_RENDA].dropna().unique(), default=df[COL_RENDA].dropna().unique())
cidade_sel = st.sidebar.multiselect("Cidade/Estado", df[COL_CIDADE].dropna().unique(), default=df[COL_CIDADE].dropna().unique())

df = df[
    (df[COL_GENERO].isin(genero_sel)) &
    (df[COL_IDADE].isin(idade_sel)) &
    (df[COL_ESCOLAR].isin(escolar_sel)) &
    (df[COL_RENDA].isin(renda_sel)) &
    (df[COL_CIDADE].isin(cidade_sel))
]

# =============================
# 4) Funções auxiliares
# =============================
def vc_table(series: pd.Series, normalize=True) -> pd.DataFrame:
    s = series.fillna("(Sem resposta)").astype(str).str.strip()
    counts = s.value_counts(dropna=False)
    if normalize:
        pct = (counts / counts.sum() * 100).round(1)
        out = pd.DataFrame({"Contagem": counts, "%": pct})
    else:
        out = pd.DataFrame({"Contagem": counts})
    out.index.name = series.name
    return out.reset_index().rename(columns={series.name: "Categoria"})

def encode_yes_no(txt: str) -> int:
    if not isinstance(txt, str):
        return 0
    t = txt.strip().lower()
    if t.startswith("s"):  # sim
        return 1
    return 0

def encode_segunda_mao(txt: str) -> int:
    if not isinstance(txt, str):
        return 0
    t = txt.strip().lower()
    if "nunca" in t:
        return 0
    if "ocas" in t or "às" in t or "as vez" in t or "eventual" in t:
        return 1
    if "freq" in t or "sempre" in t:
        return 2
    # fallback: conta como ocasional
    return 1

def build_indice_circularidade(df: pd.DataFrame) -> pd.Series:
    a = df.get(COL_RENDA, pd.Series([np.nan]*len(df))).apply(encode_yes_no)  # atenção: aqui deve ser COL_REFORMA se tiver
    b = df.get(COL_MARCA_SUST, pd.Series([np.nan]*len(df))).apply(encode_yes_no)  # se tiver
    c = df.get(COL_2MAO, pd.Series([np.nan]*len(df))).apply(encode_segunda_mao)
    idx = (a + b + c).clip(0, 3)
    return idx

CIRC_LABELS = {
    0: "Baixa (nenhuma prática)",
    1: "Ocasional (pouca prática)",
    2: "Média (práticas esporádicas)",
    3: "Alta (práticas frequentes)",
}
# =============================
# A) Perfil dos participantes
# =============================
st.header("A) Perfil dos participantes")
perfil_cols = [COL_GENERO, COL_IDADE, COL_ESCOLAR, COL_RENDA, COL_CIDADE]
for col in perfil_cols:
    st.subheader(col)
    tb = vc_table(df[col])
    tb["Categoria"] = tb["Categoria"].astype(str)
    st.dataframe(tb, use_container_width=True)
    st.altair_chart(
        alt.Chart(tb).mark_bar().encode(
            x=alt.X("Contagem:Q"),
            y=alt.Y("Categoria:N", sort='-x'),
            tooltip=["Categoria", "Contagem", "%"]
        ).properties(height=320),
        use_container_width=True
    )
###############################
# =============================
# A) Perfil dos participantes
# =============================
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
data = {
    "Cidade_Normalizada": [
        "Osvaldo Cruz", "Adamantina", "Parapuã", "Salmourão", "Lucélia", "Tupã",
        "São Paulo", "Inúbia Paulista", "Flórida Paulista", "Pacaembu", "Marília",
        "Rinópolis", "Pompéia", "Iacri", "Presidente Prudente", "Rio De Janeiro",
        "Tupi Paulista", "Lins", "Araçatuba", "Mirante Do Paranapanema", "Ourinhos",
        "Natal", "Sapucaia Do Sul", "Carapicuíba", "Quintana", "Presidente Venceslau",
        "São Gonçalo", "Campinas", "Bastos", "Herculândia", "Sete Lagoas",
        "Campos Novos Paulista", "Ribeirão Preto", "Nova Alvorada Do Sul", "Paulinia",
        "Palmas", "Mariápolis", "Volta Redonda", "Guarulhos", "Brasília", "Niterói",
        "Pracinha", "Campo Mourão", "Gabriel Monteiro", "Maringá", "Jundiai",
        "Ouro Verde", "Arco Iris"
    ],
    "Frequência": [
        75, 74, 50, 17, 13, 13, 9, 9, 9, 7, 7, 5, 5, 3, 3, 2, 2, 2, 2, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 1, 1, 1, 1, 1, 1
    ],
    "Lat": [
        -21.7963, -21.6822, -21.7771, -21.6216, -21.7182, -21.9337, -23.5505,
        -21.7697, -21.6127, -21.5628, -22.2176, -21.8304, -22.1071, -21.8571,
        -22.1207, -22.9068, -21.3828, -21.6733, -21.2081, -22.2905, -22.9774,
        -5.7945, -29.8276, -23.5225, -22.0964, -21.8753, -22.8268, -22.9056,
        -21.9287, -22.0036, -19.4653, -22.6037, -21.1775, -21.4652, -22.7665,
        -10.2095, -21.7949, -22.5200, -23.4543, -15.8267, -22.8832, -21.8531,
        -24.0465, -21.5292, -23.4262, -23.1857, -21.4879, -21.7707
    ],
    "Lon": [
        -50.8798, -51.0724, -50.6455, -50.8619, -51.0059, -50.5191, -46.6333,
        -51.2559, -51.1726, -51.2672, -49.9506, -50.7264, -50.1758, -50.6379,
        -51.3893, -43.1729, -51.5625, -49.7424, -50.4014, -51.9085, -49.8706,
        -35.2094, -51.1498, -46.8353, -50.3052, -51.8479, -43.0634, -47.0608,
        -50.7354, -50.3893, -44.2469, -49.9986, -47.8103, -54.3750, -47.1470,
        -48.3317, -51.1998, -44.1045, -46.5333, -47.9218, -43.1034, -51.0951,
        -52.3781, -50.5523, -51.9333, -46.8842, -51.7016, -50.4565
    ]
}

df_cidades = pd.DataFrame(data)

# Dados das cidades com coordenadas
df_cidades = pd.DataFrame(data)

# Criar o mapa
st.subheader("Mapa de Frequência por Cidade")
m = folium.Map(location=[-22.0, -48.0], zoom_start=6)
marker_cluster = MarkerCluster().add_to(m)

def get_color(freq):
    if freq >= 50:
        return "red"
    elif freq >= 20:
        return "orange"
    elif freq >= 10:
        return "blue"
    else:
        return "green"

for _, row in df_cidades.iterrows():
    folium.CircleMarker(
        location=[row["Lat"], row["Lon"]],
        radius=8 + (row["Frequência"] / 10),
        color=get_color(row["Frequência"]),
        fill=True,
        fill_color=get_color(row["Frequência"]),
        popup=f"{row['Cidade_Normalizada']} - {row['Frequência']}"
    ).add_to(marker_cluster)

st_folium(m, width=800, height=600)

# Estatísticas do mapa

st.subheader("📊 Estatísticas")
st.write(f"**Total de cidades:** {df_cidades['Cidade_Normalizada'].nunique()}")
st.write(f"**Frequência Total:** {df_cidades['Frequência'].sum()}")

st.dataframe(df_cidades.sort_values("Frequência", ascending=False))

########################
# =============================
# B) Frequência de compra e faixa de gasto
# =============================
st.header("B) Distribuição de Frequência de compra e faixa de gasto")
col1, col2 = st.columns(2)

with col1:
    tb_freq = vc_table(df[COL_FREQ])
    tb_freq["Categoria"] = tb_freq["Categoria"].astype(str)
    st.subheader("Frequência de compra")
    st.dataframe(tb_freq, use_container_width=True)
    st.altair_chart(
        alt.Chart(tb_freq).mark_bar().encode(
            x=alt.X("Contagem:Q"),
            y=alt.Y("Categoria:N", sort='-x'),
            tooltip=["Categoria", "Contagem", "%"]
        ).properties(height=320),
        use_container_width=True
    )

with col2:
    tb_gasto = vc_table(df[COL_GASTO])
    tb_gasto["Categoria"] = tb_gasto["Categoria"].astype(str)
    st.subheader("Faixa de gasto")
    st.dataframe(tb_gasto, use_container_width=True)
    st.altair_chart(
        alt.Chart(tb_gasto).mark_bar().encode(
            x=alt.X("Contagem:Q"),
            y=alt.Y("Categoria:N", sort='-x'),
            tooltip=["Categoria", "Contagem", "%"]
        ).properties(height=320),
        use_container_width=True
    )

# =============================
# C) Segunda mão e percepções
# =============================
st.header("C) Consumo de Segunda Mão e Percepções")
# =============================

seg_table = vc_table(df.get(COL_2MAO, pd.Series(dtype=object)))
st.dataframe(seg_table, use_container_width=True)

# Pizza (proporções)
seg_chart = alt.Chart(seg_table).transform_calculate(
    angle='datum["%"] * 2 * PI / 100',
    color_field='datum.Categoria'
).mark_arc(innerRadius=40).encode(
    theta=alt.Theta(field="%", type="quantitative"),
    color=alt.Color("Categoria:N"),
    tooltip=["Categoria", "Contagem", "%"]
).properties(height=360)
st.altair_chart(seg_chart, use_container_width=True)

##########
# Índice e categoria
idx = build_indice_circularidade(df)
df_idx = df.assign(**{"Índice de Circularidade": idx.map(CIRC_LABELS).fillna("(Indefinido)")})

cross = pd.crosstab(
    df_idx.get(COL_IMPACTO, pd.Series(dtype=object)).fillna("(Sem resposta)"),
    df_idx["Índice de Circularidade"],
    normalize="index"
).round(3) * 100
cross = cross.reset_index().rename(columns={COL_IMPACTO: "Percepção de impacto"})
st.dataframe(cross, use_container_width=True)

# Barras evidenciando distância entre discurso e ação
cross_long = cross.melt(id_vars="Percepção de impacto", var_name="Nível de prática", value_name="%")
bar_gap = alt.Chart(cross_long).mark_bar().encode(
    x=alt.X("Percepção de impacto:N"),
    y=alt.Y("%:Q"),
    color=alt.Color("Nível de prática:N"),
    tooltip=["Percepção de impacto", "Nível de prática", alt.Tooltip("%:Q", format=".1f")]
).properties(height=400)
st.altair_chart(bar_gap, use_container_width=True)



# D) Relação com os ODS
# =============================
st.header("D) Relação com os ODS")
tb_ods = vc_table(df[COL_ODS])
tb_ods["Categoria"] = tb_ods["Categoria"].astype(str)
st.dataframe(tb_ods, use_container_width=True)

# Gráfico estilo último código
ods_bar = alt.Chart(tb_ods).mark_bar().encode(
    x=alt.X("Categoria:N", sort='-y'),  # Ordena pelo total descendente
    y=alt.Y("Contagem:Q"),
    tooltip=["Categoria", "Contagem", "%"]
).properties(height=340)

st.altair_chart(ods_bar, use_container_width=True)

# =============================
# E) Motivação (nuvem de palavras)
# =============================
st.header("E) Motivação para escolhas de consumo")
st.image("nuvem.png", use_container_width=True)
