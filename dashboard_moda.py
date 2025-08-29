import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from io import BytesIO

st.set_page_config(page_title="Consumo de Moda – Dashboard", layout="wide")
st.title("📊 Consumo de Moda – Faap 2025")
st.caption("Estudo realizado pela professora Lilian Fortuna")

# =============================
# 1) Carregamento da base
# =============================

df_raw = pd.read_excel("moda.xlsx")
#st.info("Carregado automaticamente: moda.xlsx (mesma pasta do app)")

# =============================
# 2) Padronização de colunas
# =============================
# Normaliza nomes (remove espaços extras e quebra-linhas)
df = df_raw.copy()
df.columns = [c.replace("\n", " ").strip() for c in df.columns]

# Mapeamento dos nomes originais do formulário (observados no arquivo)
COL_FREQ = "Com que frequência você compra roupas novas?"
COL_GASTO = "Quanto você gasta, em média, com roupas por mês?"
COL_2MAO = "Você compra roupas de segunda mão (ex: brechós/desapegos)?"
COL_IMPACTO = "Você acredita que o consumo de moda impacta o meio ambiente?"
COL_REFORMA = "Você já reformou alguma peça de roupa antiga para torná-la mais atual?"
COL_MARCA_SUST = "Você já comprou ou conhece marcas que promovem moda sustentável?"
COL_ODS = "Você relaciona suas escolhas de vestuário com os Objetivos de Desenvolvimento Sustentável (ODS)?"

# Tenta casar variações com espaços extras
name_map = {}
for c in df.columns:
    base = c.strip().rstrip("?").rstrip(".")
    if COL_FREQ.startswith(base[:20]) and "frequência" in c:
        name_map[c] = COL_FREQ
    if COL_GASTO.startswith(base[:20]) and "gasta" in c:
        name_map[c] = COL_GASTO
    if "segunda mão" in c:
        name_map[c] = COL_2MAO
    if "impacta o meio ambiente" in c:
        name_map[c] = COL_IMPACTO
    if "reformou" in c:
        name_map[c] = COL_REFORMA
    if "moda sustentável" in c:
        name_map[c] = COL_MARCA_SUST
    if "Objetivos de Desenvolvimento Sustentável" in c:
        name_map[c] = COL_ODS

# Renomeia somente o que encontrou
for old, new in name_map.items():
    df.rename(columns={old: new}, inplace=True)

# Checagem de presença
required = [COL_FREQ, COL_GASTO, COL_2MAO, COL_IMPACTO, COL_REFORMA, COL_MARCA_SUST, COL_ODS]
missing = [c for c in required if c not in df.columns]
if missing:
    st.warning("Colunas não encontradas na planilha: " + ", ".join(missing))

# =============================
# 3) Funções utilitárias
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

# Codificação simples para índice de circularidade
#  (quanto maior, mais prática efetiva)
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

# Construção do índice (0 a 3)
def build_indice_circularidade(df: pd.DataFrame) -> pd.Series:
    a = df.get(COL_REFORMA, pd.Series([np.nan]*len(df))).apply(encode_yes_no)
    b = df.get(COL_MARCA_SUST, pd.Series([np.nan]*len(df))).apply(encode_yes_no)
    c = df.get(COL_2MAO, pd.Series([np.nan]*len(df))).apply(encode_segunda_mao)
    idx = (a + b + c).clip(0, 3)
    return idx

# Categoriza índice
CIRC_LABELS = {
    0: "Baixa (nenhuma prática)",
    1: "Ocasional (pouca prática)",
    2: "Média (práticas esporádicas)",
    3: "Alta (práticas frequentes)",
}

# =============================
# 4) Layout – Seções
# =============================
# =============================
# Filtros no Sidebar
# =============================
st.sidebar.header("Filtros")

# Seleção múltipla para faixa etária
faixa_etaria_opts = df["Qual é a sua faixa etária?"].dropna().unique()
faixa_sel = st.sidebar.multiselect("Faixa etária", faixa_etaria_opts, default=faixa_etaria_opts)

# Seleção múltipla para gênero
genero_opts = df["Qual é o seu gênero?"].dropna().unique()
genero_sel = st.sidebar.multiselect("Gênero", genero_opts, default=genero_opts)

# Seleção múltipla para renda
renda_opts = df["Qual é sua faixa de renda mensal?"].dropna().unique()
renda_sel = st.sidebar.multiselect("Faixa de renda", renda_opts, default=renda_opts)

# Seleção múltipla para cidade
cidade_opts = df["Qual a sua cidade e estado?"].dropna().unique()
cidade_sel = st.sidebar.multiselect("Cidade/Estado", cidade_opts, default=cidade_opts)

# Aplicar os filtros
df = df[
    (df["Qual é a sua faixa etária?"].isin(faixa_sel)) &
    (df["Qual é o seu gênero?"].isin(genero_sel)) &
    (df["Qual é sua faixa de renda mensal?"].isin(renda_sel)) &
    (df["Qual a sua cidade e estado?"].isin(cidade_sel))
]
# =============================
# Seção A – Distribuições básicas
# =============================
st.subheader("A) Distribuição de Frequência de Compra e Faixa de Gasto")
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Frequência de compra**")
    tb_freq = vc_table(df.get(COL_FREQ, pd.Series(dtype=object)))
    st.dataframe(tb_freq, use_container_width=True)
    chart_freq = alt.Chart(tb_freq).mark_bar().encode(
        x=alt.X("Contagem:Q"),
        y=alt.Y("Categoria:N", sort='-x'),
        tooltip=["Categoria", "Contagem", "%"]
    ).properties(height=320)
    st.altair_chart(chart_freq, use_container_width=True)

with col2:
    st.markdown("**Faixas de gasto mensal**")
    tb_gasto = vc_table(df.get(COL_GASTO, pd.Series(dtype=object)))
    st.dataframe(tb_gasto, use_container_width=True)
    chart_gasto = alt.Chart(tb_gasto).mark_bar().encode(
        x=alt.X("Contagem:Q"),
        y=alt.Y("Categoria:N", sort='-x'),
        tooltip=["Categoria", "Contagem", "%"]
    ).properties(height=320)
    st.altair_chart(chart_gasto, use_container_width=True)

# Gráfico de colunas comparando perfis (freq x gasto)
st.markdown("**Comparação de perfis de consumo (Frequência × Gasto)**")
ct = pd.crosstab(
    df.get(COL_FREQ, pd.Series(dtype=object)).fillna("(Sem resposta)"),
    df.get(COL_GASTO, pd.Series(dtype=object)).fillna("(Sem resposta)")
)
ct_reset = ct.reset_index().melt(id_vars=ct.index.name, var_name="Faixa de gasto", value_name="Contagem")
bar_group = alt.Chart(ct_reset).mark_bar().encode(
    x=alt.X("Faixa de gasto:N", sort="-y"),
    y=alt.Y("Contagem:Q"),
    color=alt.Color(f"{ct.index.name}:N"),
    tooltip=[ct.index.name, "Faixa de gasto", "Contagem"]
).properties(height=380)
st.altair_chart(bar_group, use_container_width=True)

# =============================
# Seção B – Consumo de segunda mão
# =============================
st.subheader("B) Consumo de Segunda Mão")
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

# =============================
# Seção C – Percepção ambiental × práticas de circularidade
# =============================
st.subheader("C) Percepção Ambiental × Práticas de Circularidade")
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

# =============================
# Seção D – ODS e moda
# =============================
st.subheader("D) Relação com os ODS")
ods_tab = vc_table(df.get(COL_ODS, pd.Series(dtype=object)))
st.dataframe(ods_tab, use_container_width=True)

ods_bar = alt.Chart(ods_tab).mark_bar().encode(
    x=alt.X("Categoria:N", sort='-y'),
    y=alt.Y("Contagem:Q"),
    tooltip=["Categoria", "Contagem", "%"]
).properties(height=340)
st.altair_chart(ods_bar, use_container_width=True)

# =============================
# 5) Downloads das tabelas
# =============================
with st.expander("⬇️ Baixar tabelas (CSV)"):
    btn_cols = st.columns(4)
    def dl(df_, label):
        csv = df_.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=f"Baixar {label}",
            data=csv,
            file_name=f"{label.replace(' ', '_').lower()}.csv",
            mime="text/csv",
            use_container_width=True,
            key=label
        )
    with btn_cols[0]:
        dl(tb_freq, "tabela_frequencia_compra")
    with btn_cols[1]:
        dl(tb_gasto, "tabela_faixa_gasto")
    with btn_cols[2]:
        dl(seg_table, "tabela_segunda_mao")
    with btn_cols[3]:
        dl(ods_tab, "tabela_ods")

st.caption("© Dashboard educativo – Streamlit + Pandas + Altair")



# =============================
import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# ======================
# Dados das cidades com coordenadas
# ======================
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

df = pd.DataFrame(data)

# ======================
# Criar o mapa
# ======================
st.title("📍 Mapa de Frequência por Cidade")

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

for _, row in df.iterrows():
    folium.CircleMarker(
        location=[row["Lat"], row["Lon"]],
        radius=8 + (row["Frequência"] / 10),
        color=get_color(row["Frequência"]),
        fill=True,
        fill_color=get_color(row["Frequência"]),
        popup=f"{row['Cidade_Normalizada']} - {row['Frequência']}"
    ).add_to(marker_cluster)

st_folium(m, width=800, height=600)

# ======================
# Estatísticas
# ======================
st.subheader("📊 Estatísticas")
st.write(f"**Total de cidades:** {df['Cidade_Normalizada'].nunique()}")
st.write(f"**Frequência Total:** {df['Frequência'].sum()}")

st.dataframe(df.sort_values("Frequência", ascending=False))
