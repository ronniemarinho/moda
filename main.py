import streamlit as st
import pandas as pd
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import DBSCAN
from mlxtend.frequent_patterns import apriori, association_rules
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, mean_absolute_error

st.set_page_config(layout="wide")
st.title("Análise de Dados de Consumo de Moda")

# Leitura do arquivo CSV diretamente
df = pd.read_csv('moda_lilian.csv')

# Limpeza e padronização dos nomes das colunas
df.columns = df.columns.str.strip()

# Exibir as primeiras linhas da base
st.subheader("Base de Dados")
st.write(df.head())

# Nuvem de Palavras
st.subheader("Nuvem de Palavras - Comentários de Compra")

# Obter o nome exato da coluna
coluna_motivacao = [col for col in df.columns if 'motiva' in col.lower()][0]

comments = df[coluna_motivacao]
text = " ".join(str(comment) for comment in comments)

wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

plt.figure(figsize=(15, 7))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
st.pyplot(plt)

# Pré-processamento para Clustering
st.subheader("Agrupamento de Consumidores (DBSCAN)")

clustering_data = df[['Qual é a sua faixa etária?', 'Qual é o seu gênero?',
                      'Você compra roupas de segunda mão (ex: brechós/desapegos)?',
                      'Você conhece o conceito de moda circular?',
                      'Você se considera um(a) consumidor(a) consciente? Por quê?']].copy()

# Codificando variáveis categóricas
for col in clustering_data.columns:
    clustering_data[col] = LabelEncoder().fit_transform(clustering_data[col].astype(str))

scaler = StandardScaler()
clustering_data_scaled = scaler.fit_transform(clustering_data)

dbscan = DBSCAN(eps=1.5, min_samples=2)
clusters = dbscan.fit_predict(clustering_data_scaled)

df['Cluster'] = clusters
st.write(df[['Qual é a sua faixa etária?', 'Qual é o seu gênero?', 'Cluster']])

st.write("Número de clusters encontrados:", len(set(clusters)) - (1 if -1 in clusters else 0))

# Apriori - Associação de Hábitos
st.subheader("Associações entre Hábitos de Consumo (Apriori)")

association_data = df[['Você compra roupas de segunda mão (ex: brechós/desapegos)?',
                       'Você costuma alugar roupas para eventos ou ocasiões especiais?',
                       'Você conhece o conceito de moda circular?',
                       'Você estaria disposto(a) a pagar mais por roupas feitas de forma sustentável ou com materiais reciclados?']]

# Transformar respostas em True/False
association_data = association_data.applymap(lambda x: True if str(x).lower() in ['sim', 'sim.'] else False)

frequent_itemsets = apriori(association_data, min_support=0.2, use_colnames=True)
rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1)

st.write("Regras de Associação Encontradas:")
st.write(rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']])

# Previsão de Comportamento - Random Forest
st.subheader("Previsão de Consumo Consciente")

classification_data = df.dropna()

X = classification_data[['Qual é a sua faixa etária?', 'Qual é o seu gênero?',
                         'Você compra roupas de segunda mão (ex: brechós/desapegos)?',
                         'Você conhece o conceito de moda circular?',
                         'Você gosta de comprar as suas roupas em lojas físicas ou pela internet?']]

y = classification_data['Você se considera um(a) consumidor(a) consciente? Por quê?']

# Codificação
for col in X.columns:
    X[col] = LabelEncoder().fit_transform(X[col].astype(str))
y = LabelEncoder().fit_transform(y.astype(str))

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

clf = RandomForestClassifier()
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)

st.write("Relatório de Classificação:")
st.text(classification_report(y_test, y_pred))

# Previsão de Gasto Mensal
st.subheader("Previsão de Gasto Mensal com Roupas")

regression_data = df.dropna()

X_reg = regression_data[['Qual é a sua faixa etária?', 'Qual é o seu gênero?',
                         'Você compra roupas de segunda mão (ex: brechós/desapegos)?',
                         'Você conhece o conceito de moda circular?',
                         'Você gosta de comprar as suas roupas em lojas físicas ou pela internet?']]

y_reg = regression_data['Quanto você gasta, em média, com roupas por mês?']

# Codificação
for col in X_reg.columns:
    X_reg[col] = LabelEncoder().fit_transform(X_reg[col].astype(str))
y_reg = LabelEncoder().fit_transform(y_reg.astype(str))

X_train_reg, X_test_reg, y_train_reg, y_test_reg = train_test_split(X_reg, y_reg, test_size=0.2, random_state=42)

reg = RandomForestRegressor()
reg.fit(X_train_reg, y_train_reg)
y_pred_reg = reg.predict(X_test_reg)

st.write("Erro médio absoluto (MAE) da previsão de gasto mensal:")
st.write(mean_absolute_error(y_test_reg, y_pred_reg))
