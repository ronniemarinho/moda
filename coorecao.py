from collections import Counter

# Cole aqui sua lista de cidades
cities = """
Pacaembu
Adamantina
Pacaembu
Pacaembu
Adamantina
Adamantina
Adamantina
Adamantina
Adamantina
Lucélia
Adamantina
Adamantina
Adamantina
Adamantina
Rinópolis
Adamantina
Pacaembu
Adamantina
Tupã
Tupã
Mirante do Paranapanema
Ourinhos
Natal
São Paulo
Tupã
Salmourão
Adamantina
Rio de Janeiro
Tupi Paulista
Osvaldo Cruz
Iacri
Osvaldo Cruz
Marília
Sapucaia do Sul
Parapuã
Presidente Prudente
Osvaldo Cruz
Inúbia Paulista
Tupi Paulista
Parapuã
Carapicuíba
Quintana
Osvaldo Cruz
Osvaldo Cruz
Adamantina
Parapuã
Adamantina
Presidente Venceslau
Lins
Osvaldo Cruz
Parapuã
Parapuã
Adamantina
Pompéia
Osvaldo cruz
Parapuã
Osvaldo Cruz
Parapuã
Adamantina
Adamantina
Flórida Paulista
Parapuã
São Gonçalo
Flórida paulista
Osvaldo Cruz
Adamantina
Campinas
Parapuã
Pompéia
Presidente Prudente
Parapuã
Parapuã
Adamantina
Parapuã
Bastos
Flórida Paulista
Herculândia
Adamantina
Adamantina
Parapuã
Osvaldo Cruz
Osvaldo Cruz
Osvaldo Cruz
Parapuã
Adamantina
Sete Lagoas
Parapuã
Marília
Inúbia Paulista
Inúbia Paulista
Lucélia
Osvaldo Cruz
Osvaldo Cruz
Osvaldo Cruz
Osvaldo Cruz
Osvaldo Cruz
Araçatuba
Campos Novos Paulista
Pompéia
Adamantina
Osvaldo Cruz
Marília
Pompéia
Inúbia Paulista
Osvaldo Cruz
Ribeirão Preto
Tupã
Osvaldo Cruz
Tupã
Tupã
Marília
Adamantina
Tupã
Parapuã
Tupã
Salmourão
Parapuã
Osvaldo Cruz
Salmourão
Parapuã
Osvaldo Cruz
Nova Alvorada do Sul
Marília
Salmourão
Iacri
Osvaldo Cruz
Inúbia Paulista
Inúbia Paulista
Inúbia Paulista
Adamantina
Rinópolis
Adamantina
Paulinia
Lucélia
Osvaldo Cruz
Inúbia Paulista
Palmas
Osvaldo cruz
Lucélia
Mariápolis
Parapuã
São Paulo
Parapuã
Volta Redonda
Parapuã
Adamantina
Flórida Paulista
Parapuã
Guarulhos
Parapuã
Osvaldo Cruz
Parapuã
Parapuã
Iacri
Salmourāo
Tupã
Osvaldo Cruz
Rinópolis
Parapuã
Parapuã
Parapuã
Salmourão
Parapuã
Parapuã
Brasília
Adamantina
Parapuã
Pompéia
Parapuã
Osvaldo Cruz
Salmourão
Osvaldo Cruz
Osvaldo Cruz
Osvaldo Cruz
Parapuã
Adamantina
Rinópolis
Adamantina
Presidente Prudente
Osvaldo Cruz
Osvaldo Cruz
Lucélia
Adamantina
Lucélia
Adamantina
Osvaldo cruz
Parapuã
Niterói
Parapuã
Pracinha
Campo Mourão
Adamantina
Parapuã
Osvaldo Cruz
Parapuã
Gabriel Monteiro
Maringá 
Osvaldo Cruz
Flórida Paulista
Osvaldo Cruz
Tupã
Jundiai
Osvaldo Cruz
São Paulo
Parapuã
Osvaldo Cruz
Adamantina
Salmourão
Salmourão
Osvaldo Cruz
Lucélia
São Paulo
Marília
Salmourão
Adamantina
Osvaldo Cruz
Salmourão
Lins
Salmourão
São Paulo
Adamantina
Adamantina
Adamantina
Adamantina
Pacaembu
Osvaldo Cruz
Rio de Janeiro
Lucélia
Adamantina
Osvaldo Cruz
São Paulo
Salmourão
Adamantina
São Paulo
Adamantina
Adamantina
Ouro Verde
Adamantina
São Paulo
Adamantina
Adamantina
Lucélia
Salmourão
Osvaldo Cruz
Osvaldo Cruz
Adamantina
Osvaldo Cruz
Osvaldo Cruz
Tupã
Osvaldo Cruz
Osvaldo Cruz
Adamantina
Osvaldo Cruz
Osvaldo Cruz
Osvaldo Cruz
Osvaldo Cruz
Adamantina
Lucélia
Parapuã
Osvaldo Cruz
Osvaldo Cruz
Adamantina
Osvaldo Cruz
Osvaldo Cruz
Flórida Paulista
Osvaldo Cruz
Adamantina
Osvaldo Cruz
Osvaldo Cruz
Osvaldo Cruz
Osvaldo Cruz
Adamantina
Adamantina
Osvaldo Cruz
Flórida Paulista
Osvaldo Cruz
Adamantina
Osvaldo Cruz
Adamantina
Osvaldo Cruz
Pacaembu
Adamantina
Salmourão
Tupã
Osvaldo Cruz
Adamantina
Parapuã
Lucélia
Adamantina
Adamantina
Lucélia
Adamantina
Adamantina
Lucélia
Osvaldo cruz
Osvaldo Cruz
Adamantina
Osvaldo Cruz
Osvaldo Cruz
Osvaldo Cruz
Osvaldo Cruz
São Paulo
Tupã
Adamantina
Adamantina
Adamantina
Inúbia Paulista
Osvaldo Cruz
Osvaldo Cruz
Adamantina
Arco Iris
Flórida Paulista
Parapuã
Parapuã
Parapuã
Rinópolis
Parapuã
Parapuã
Salmourão
Parapuã
Parapuã
Parapuã
Parapuã
Parapuã
Adamantina
Adamantina
Adamantina
Pacaembu
Flórida Paulista
Adamantina
Adamantina
Adamantina
Salmourão
Araçatuba
Marília
Adamantina
""".strip().split('\n')

# Normalização dos nomes (acentuação, capitalização, variantes como "Osvaldo cruz")
cities_normalized = [
    c.strip().title().replace("Salmourāo", "Salmourão").replace("Flórida paulista", "Flórida Paulista").replace("Osvaldo cruz", "Osvaldo Cruz")
    for c in cities
]

# Contagem das cidades
city_counts = Counter(cities_normalized)

# Exibir resultado em forma de tabela
print("{:<30} | {:>5}".format("Cidade", "Frequência"))
print("-" * 40)
for city, count in city_counts.most_common():
    print(f"{city:<30} | {count:>5}")
