# ODS4 — Data Lakehouse INEP 🎓

> Pipeline de dados do **Censo Escolar da Educação Básica (INEP)** organizado na arquitetura **Medallion** (Raw → Bronze → Silver → Gold), desenvolvido como produto da Extensão Curricularizada do curso de Análise e Desenvolvimento de Sistemas (ADS).

---

## 📌 Objetivo

Transformar os microdados brutos do Censo Escolar INEP (2007–2024) em tabelas analíticas prontas para uso em painéis de visualização (Power BI, Metabase, Looker, etc.), com colunas normalizadas, nomes legíveis e dados limpos.

---

## 🏗️ Arquitetura — Medallion Lakehouse

```
data/
├── raw/       ← ZIPs originais baixados do INEP (não versionados)
├── bronze/    ← CSVs extraídos dos ZIPs, particionados por ano
│              └── ano=YYYY/microdados_ed_basica_YYYY.csv
├── silver/    ← Parquet normalizados: colunas em snake_case, tipos corretos
│              └── microdados_escola/ano=YYYY/microdados_escola.parquet
└── gold/      ← Tabelas analíticas prontas para painel
               ├── dim_escola.parquet
               ├── fct_matriculas_por_escola_ano.parquet
               └── fct_docentes_turmas_por_escola_ano.parquet
```

### Camadas

| Camada | Descrição | Formato | Partição |
|--------|-----------|---------|----------|
| **Raw** | ZIPs originais do INEP, sem modificação | `.zip` | — |
| **Bronze** | CSVs extraídos, sem transformação | `.csv` | `ano=YYYY` |
| **Silver** | Dados limpos, tipados e com nomes normalizados | `.parquet` | `ano=YYYY` |
| **Gold** | Tabelas analíticas agregadas, prontas para BI | `.parquet` | — |

---

## 📁 Estrutura do Repositório

```
ods4-data-lakehouse-inep/
├── data/                          # Dados (não versionados, ver .gitignore)
│   ├── raw/                       # ZIPs originais do INEP
│   ├── bronze/                    # CSVs extraídos
│   ├── silver/                    # Parquet normalizados
│   └── gold/                      # Tabelas Gold para painel
│
├── notebooks/                     # Notebooks Jupyter por camada
│   ├── bronze/
│   │   ├── zip_to_file.ipynb      # Extração ZIPs → Bronze
│   │   └── raw_to_bronze.ipynb    # Validação da camada Bronze
│   ├── silver/
│   │   └── bronze_to_silver.ipynb # Pipeline Bronze → Silver
│   └── gold/
│       └── silver_to_gold.ipynb   # Pipeline Silver → Gold + exemplos de análise
│
├── src/                           # Código-fonte Python
│   ├── config/
│   │   └── settings.py            # Caminhos e configurações via variáveis de ambiente
│   ├── jobs/
│   │   ├── bronze/
│   │   │   ├── ingest_from_web.py     # ✨ Download direto INEP (web) → Bronze
│   │   │   ├── zip_to_file.py         # Extração de ZIPs locais → Bronze
│   │   │   └── raw_to_bronze.py       # Validação: Bronze
│   │   ├── silver/
│   │   │   └── bronze_to_silver.py # Transformação: Bronze → Silver
│   │   └── gold/
│   │       └── silver_to_gold.py  # Agregação: Silver → Gold
│   └── utils/
│       └── logger.py              # Logger padrão do projeto
│
├── tests/                         # Testes automatizados
│   ├── conftest.py                # Fixtures compartilhadas (caminhos)
│   ├── test_bronze.py             # Validações da camada Bronze
│   ├── test_silver.py             # Validações da camada Silver
│   └── test_gold.py               # Validações da camada Gold
│
├── docs/
│   ├── dicionario_de_dados.md     # Descrição das colunas das tabelas Gold
│   └── guia_databricks.md         # Como rodar o pipeline no Databricks
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🚀 Como executar

### 1. Pré-requisitos

- Python 3.10+
- Virtualenv

```bash
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

### 2. Preparar os dados brutos

#### Opção A — Download automático direto do INEP (recomendado)

Baixa os ZIPs diretamente do servidor do INEP sem precisar de arquivos locais:

```bash
python -m src.jobs.bronze.ingest_from_web
```

Por padrão, baixa os anos **2004–2024** (pulando 2020, sem publicação). Anos já baixados são pulados automaticamente (idempotente).

#### Opção B — ZIPs locais

Se preferir baixar manualmente, coloque os ZIPs em `data/raw/` com os nomes:
```
microdados_censo_escolar_{ano}.zip
microdados_censo_escolar_{ano}_.zip   ← variante com underscore (2025+)
```

E execute:
```bash
python -m src.jobs.bronze.zip_to_file
```

### 3. Executar o pipeline completo

```bash
# Etapa 1 — Baixar dados do INEP direto da web (2004–2024)
python -m src.jobs.bronze.ingest_from_web

# Etapa 2 — Normalizar Bronze para Silver (demora ~1.5h para todos os anos)
python -m src.jobs.silver.bronze_to_silver

# Etapa 3 — Gerar tabelas Gold (~15min)
python -m src.jobs.gold.silver_to_gold
```

---

## ☁️ Executando no Databricks

Para rodar o pipeline no Databricks (Community, AWS, Azure ou GCP) sem precisar de arquivos locais, consulte o guia completo:

📄 **[docs/guia_databricks.md](docs/guia_databricks.md)**

Resumo rápido:
1. Conecte o repositório via **Git Repos**
2. Configure variáveis de ambiente com os caminhos DBFS/Volume
3. Crie 3 Jobs em **Workflows** (um por etapa)
4. Execute o pipeline — os dados são baixados diretamente do INEP

### 4. Executar os testes

```bash
pytest tests/ -v
```

---

## 📊 Tabelas Gold

### `dim_escola.parquet`
Dimensão de escolas com dados cadastrais. **295.907 escolas únicas** (última observação disponível por escola).

### `fct_matriculas_por_escola_ano.parquet`
Fato com matrículas por escola/ano. **3.834.235 registros** (2007–2024, exceto 2020).
Colunas: matrículas por nível de ensino, sexo e raça/cor.

### `fct_docentes_turmas_por_escola_ano.parquet`
Fato com docentes, turmas e infraestrutura por escola/ano. **3.834.235 registros**.

> 📄 Consulte o [Dicionário de Dados](docs/dicionario_de_dados.md) para descrição completa de todas as colunas.

---

## 🔧 Configuração via variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto para sobrescrever os caminhos padrão:

```env
BRONZE_DATA_PATH=/caminho/personalizado/para/bronze
SILVER_DATA_PATH=/caminho/personalizado/para/silver
GOLD_DATA_PATH=/caminho/personalizado/para/gold
```

---

## 📦 Dependências

| Pacote | Uso |
|--------|-----|
| `pandas` | Processamento dos dados |
| `pyarrow` | Leitura/escrita de Parquet |
| `python-dotenv` | Variáveis de ambiente |
| `pytest` | Testes automatizados |
| `pyspark` | Legado (estrutura original do projeto) |

---

## 📚 Fonte dos Dados

**INEP — Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira**
- Censo Escolar da Educação Básica — Microdados
- Cobertura: 2007 a 2024 (exceto 2020, sem publicação)
- Licença: Dados públicos, uso livre para fins educacionais e de pesquisa
- [Portal de dados abertos](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-escolar)
