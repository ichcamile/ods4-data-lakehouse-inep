# Guia de Implantação no Databricks

> Como configurar e executar o pipeline ODS4 — Data Lakehouse INEP no Databricks Community Edition ou Databricks na nuvem (AWS/Azure/GCP).

---

## Pré-requisitos

- Conta no [Databricks](https://community.cloud.databricks.com/) (Community Edition é suficiente para desenvolvimento)
- Repositório GitHub conectado ao Databricks (Git Repos)
- Cluster configurado com Python 3.10+

---

## 1. Conectar o Repositório ao Databricks

No Databricks, acesse **Workspace → Repos → Add Repo** e informe a URL do repositório:

```
https://github.com/SEU_USUARIO/ods4-data-lakehouse-inep
```

Isso cria uma cópia sincronizada do projeto em `/Repos/SEU_EMAIL/ods4-data-lakehouse-inep`.

---

## 2. Criar e Configurar o Cluster

Acesse **Compute → Create Cluster** e configure:

| Parâmetro | Valor recomendado |
|-----------|------------------|
| Runtime | `14.x LTS` ou superior |
| Node type | `Standard_DS3_v2` (Azure) / `m5.xlarge` (AWS) |
| Termination | 30 minutos de inatividade |

### Instalar dependências no cluster

Em **Libraries → Install New → PyPI**, instale:

```
pyarrow>=14.0.0
python-dotenv>=1.0.0
```

> `pandas` já vem pré-instalado no runtime do Databricks.

---

## 3. Configurar os Caminhos de Dados (DBFS ou Volume)

Em **Compute → Seu Cluster → Edit → Advanced Options → Spark → Environment Variables**, defina:

### Opção A — DBFS (mais simples, Community Edition)

```
BRONZE_DATA_PATH=/dbfs/FileStore/lakehouse_inep/bronze
SILVER_DATA_PATH=/dbfs/FileStore/lakehouse_inep/silver
GOLD_DATA_PATH=/dbfs/FileStore/lakehouse_inep/gold
```

### Opção B — Unity Catalog Volume (recomendado para produção)

```
BRONZE_DATA_PATH=/Volumes/main/lakehouse_inep/bronze
SILVER_DATA_PATH=/Volumes/main/lakehouse_inep/silver
GOLD_DATA_PATH=/Volumes/main/lakehouse_inep/gold
```

> **Importante:** sem essas variáveis, o pipeline usa os caminhos locais padrão (`data/bronze`, `data/silver`, `data/gold`) definidos no `settings.py`.

---

## 4. Jobs do Pipeline

O pipeline possui **3 jobs** que devem ser executados em sequência:

```
[Job 1] ingest_from_web  →  Bronze   (~2–4h)
[Job 2] bronze_to_silver →  Silver   (~1.5–3h)
[Job 3] silver_to_gold   →  Gold     (~15–30min)
```

Cada job **já inclui bootstrap automático de `sys.path`**, então os imports `from src.*` funcionam corretamente quando executados como Python Script no Databricks — sem necessidade de configuração extra.

---

## 5. Criar os Jobs no Databricks

Acesse **Workflows → Jobs → Create Job**.

---

### Job 1 — Ingestão INEP (Web → Bronze)

Baixa os ZIPs diretamente do servidor do INEP (sem arquivos locais) e extrai os CSVs para o Bronze.

| Campo | Valor |
|-------|-------|
| Task name | `01_ingest_from_web` |
| Type | **Python script** |
| Path | `/Repos/SEU_EMAIL/ods4-data-lakehouse-inep/src/jobs/bronze/ingest_from_web.py` |
| Cluster | Cluster configurado no passo 2 |

**URLs baixadas automaticamente (2004–2024):**
```
https://download.inep.gov.br/dados_abertos/microdados_censo_escolar_{ano}.zip
```

> Anos já baixados são **pulados automaticamente** (idempotente). O ano 2020 é ignorado (sem publicação pelo INEP).

**Tempo estimado:** ~2–4 horas.

---

### Job 2 — Normalização (Bronze → Silver)

Lê os CSVs do Bronze, normaliza para `snake_case`, converte tipos e salva em Parquet.

| Campo | Valor |
|-------|-------|
| Task name | `02_bronze_to_silver` |
| Type | **Python script** |
| Path | `/Repos/SEU_EMAIL/ods4-data-lakehouse-inep/src/jobs/silver/bronze_to_silver.py` |
| Depends on | `01_ingest_from_web` |
| Cluster | Cluster configurado no passo 2 |

**Saída:**
```
$SILVER_DATA_PATH/microdados_escola/ano=YYYY/microdados_escola.parquet
```

**Tempo estimado:** ~1.5–3 horas.

---

### Job 3 — Agregação (Silver → Gold)

Lê a Silver e gera as 3 tabelas analíticas prontas para painel.

| Campo | Valor |
|-------|-------|
| Task name | `03_silver_to_gold` |
| Type | **Python script** |
| Path | `/Repos/SEU_EMAIL/ods4-data-lakehouse-inep/src/jobs/gold/silver_to_gold.py` |
| Depends on | `02_bronze_to_silver` |
| Cluster | Cluster configurado no passo 2 |

**Saída:**
```
$GOLD_DATA_PATH/dim_escola.parquet
$GOLD_DATA_PATH/fct_matriculas_por_escola_ano.parquet
$GOLD_DATA_PATH/fct_docentes_turmas_por_escola_ano.parquet
```

**Tempo estimado:** ~15–30 minutos.

---

## 6. Pipeline Multi-Task (encadeado)

Para encadear automaticamente os 3 jobs:

1. Acesse **Workflows → Jobs → Create Job**
2. Clique em **Add task** e adicione as 3 tasks na ordem
3. Defina dependências: `02` depende de `01`, `03` depende de `02`
4. Configure o cluster compartilhado para todas as tasks
5. Salve e clique em **Run now**

### Diagrama do pipeline

```
┌─────────────────────────────┐
│  01_ingest_from_web         │  Download ZIPs INEP (2004–2024)
│  Bronze · ~2–4h             │  sem arquivos locais
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  02_bronze_to_silver        │  Normaliza colunas → Parquet
│  Silver · ~1.5–3h           │  snake_case, tipagem, nulos
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  03_silver_to_gold          │  dim_escola + 2 fatos
│  Gold · ~15–30min           │  prontas para painel
└─────────────────────────────┘
```

---

## 7. Consumir as Tabelas Gold em Notebooks

Após os jobs concluírem, leia as tabelas Gold em qualquer notebook:

```python
import pandas as pd

gold_path = "/dbfs/FileStore/lakehouse_inep/gold"

dim_escola    = pd.read_parquet(f"{gold_path}/dim_escola.parquet")
fct_matriculas = pd.read_parquet(f"{gold_path}/fct_matriculas_por_escola_ano.parquet")
fct_docentes  = pd.read_parquet(f"{gold_path}/fct_docentes_turmas_por_escola_ano.parquet")

# Exemplo: matrículas por UF no último ano
ano_max = fct_matriculas["ano_censo"].max()
(
    fct_matriculas[fct_matriculas["ano_censo"] == ano_max]
    .merge(dim_escola[["cod_escola", "uf_sigla"]], on="cod_escola")
    .groupby("uf_sigla")["qt_matriculas_total"]
    .sum()
    .sort_values(ascending=False)
)
```

---

## 8. Agendar Execução Anual (Cron)

O INEP publica os dados do ano anterior normalmente em fevereiro. Para agendar:

Em **Workflows → Jobs → Seu Job → Edit Schedule**:

```
Cron: 0 6 1 2 *   # 1º de fevereiro às 06h
```

---

## 9. Variáveis de Ambiente via Notebook (alternativa)

Se preferir notebooks ao invés de Jobs como Python Script:

```python
import os, sys

# Caminhos de dados
os.environ["BRONZE_DATA_PATH"] = "/dbfs/FileStore/lakehouse_inep/bronze"
os.environ["SILVER_DATA_PATH"] = "/dbfs/FileStore/lakehouse_inep/silver"
os.environ["GOLD_DATA_PATH"]   = "/dbfs/FileStore/lakehouse_inep/gold"

# Importar o job e executar
sys.path.insert(0, "/Workspace/Repos/SEU_EMAIL/ods4-data-lakehouse-inep")

from src.jobs.bronze.ingest_from_web import run as ingest
from src.jobs.silver.bronze_to_silver import run as silver
from src.jobs.gold.silver_to_gold import run as gold

ingest()   # Job 1
silver()   # Job 2
gold()     # Job 3
```

---

## 10. Troubleshooting

### `ModuleNotFoundError: No module named 'src'`

> ✅ **Este erro já está corrigido** nos scripts do projeto. Cada job contém um bloco de bootstrap automático:
>
> ```python
> _PROJECT_ROOT = Path(__file__).resolve().parents[3]
> if str(_PROJECT_ROOT) not in sys.path:
>     sys.path.insert(0, str(_PROJECT_ROOT))
> ```
>
> Se persistir, verifique se o repositório foi clonado corretamente via **Git Repos** e se o caminho no Job está exato.

### `ModuleNotFoundError: No module named 'src.utils.spark'`

> ✅ **Este módulo foi removido.** O pipeline usa apenas `pandas` — sem PySpark ou `get_spark_session()`. Faça `git pull` para garantir que está na versão mais recente.

### Timeout no download

Os arquivos do INEP têm 200–400 MB cada. Se houver timeout:
- Aumente o parâmetro `timeout` em `_download_e_extrair()` (padrão: 300s)
- Execute o job em horários de menor tráfego

### `FileNotFoundError` nos caminhos

Confirme que as variáveis de ambiente estão definidas no cluster:
**Compute → Seu Cluster → Edit → Advanced Options → Spark → Environment Variables**

### Ano 2020 faltando

O INEP não publicou dados de 2020. O job trata isso automaticamente — é comportamento esperado.

---

## Referências

| Recurso | Link |
|---------|------|
| Portal de Microdados INEP | https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-escolar |
| Databricks Community | https://community.cloud.databricks.com/ |
| Databricks Repos (Git) | https://docs.databricks.com/repos/index.html |
| DBFS Guide | https://docs.databricks.com/dbfs/index.html |
| Unity Catalog Volumes | https://docs.databricks.com/data-governance/unity-catalog/create-volumes.html |
| Dicionário de Dados Gold | [dicionario_de_dados.md](dicionario_de_dados.md) |
