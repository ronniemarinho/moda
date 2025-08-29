import pandas as pd
import nltk
from nltk.corpus import stopwords
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import re

# Baixar stopwords
nltk.download('stopwords')
stop_words = set(stopwords.words('portuguese'))

# Leitura da base de dados
df = pd.read_csv('moda_lilian.csv')

# Tratamento das colunas: remover quebras de linha e espaços extras
df.columns = df.columns.str.replace('\n', ' ').str.strip()

# Conferir o nome das colunas tratadas
print("Colunas disponíveis:", df.columns)

# Lista das colunas de interesse
colunas = [
    'O que te motiva a comprar roupas novas? (Ex: necessidade, estilo, promoção, rede social, entre outros)',
    'Você se considera um(a) consumidor(a) consciente? Por quê?',
    'Qual ou quais são as marcas de roupas que você mais gosta de comprar?'
]

# Nome da coluna de gênero (ajuste se estiver diferente na sua base)
coluna_genero = 'Qual é o seu gênero?'

# Função para limpar o texto
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-ZÀ-ÿ\s]', '', text)  # Remover pontuações
    words = [word for word in text.split() if word not in stop_words]
    return words

# Palavras que você quer remover de cada coluna
remover_palavras = {
    'O que te motiva a comprar roupas novas? (Ex: necessidade, estilo, promoção, rede social, entre outros)':
        ['roupas', 'comprar', 'ex', 'promoção'],
    'Você se considera um(a) consumidor(a) consciente? Por quê?': ['consumidor', 'consumidora', 'porque'],
    'Qual ou quais são as marcas de roupas que você mais gosta de comprar?': ['roupas', 'comprar', 'marcas', 'gosto', 'marca', 'compro', 'preferência', 'ligo', 'qualidade', 'bem', 'específica', 'roupa', 'sei', 'uso', 'sim']
}

# Analisar para cada coluna e para cada gênero
for col in colunas:
    print(f"\nProcessando a coluna: {col}")

    # Filtrar os gêneros únicos na base
    generos_unicos = df[coluna_genero].dropna().unique()

    for genero in generos_unicos:
        print(f"\nAnalisando o gênero: {genero}")

        # Filtrar os dados apenas para o gênero atual
        df_genero = df[df[coluna_genero] == genero]

        # Concatenar os textos da coluna
        text_data = ' '.join(df_genero[col].dropna().astype(str))

        # Limpar e tokenizar o texto
        words = clean_text(text_data)

        # Remover palavras personalizadas
        palavras_excluir = remover_palavras.get(col, [])
        words = [word for word in words if word not in palavras_excluir]

        # Contar frequência das palavras
        word_freq = Counter(words)

        if len(word_freq) == 0:
            print("Sem palavras relevantes para este gênero.")
            continue

        # Gerar a nuvem de palavras
        wordcloud = WordCloud(width=800, height=400, background_color='white',
                              colormap='viridis').generate_from_frequencies(word_freq)

        # Exibir a nuvem de palavras
        plt.figure(figsize=(15, 7))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(f'Nuvem de Palavras - {col} - Gênero: {genero}', fontsize=20)
        plt.show()

        # Exibir as 15 palavras mais citadas
        print(f"\nPalavras mais citadas - {col} - Gênero: {genero}\n")
        freq_df = pd.DataFrame(word_freq.most_common(15), columns=['Palavra', 'Frequência'])
        print(freq_df)
