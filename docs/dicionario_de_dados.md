# Dicionário de Dados — Tabelas Gold

> Camada Gold do pipeline ODS4 — Data Lakehouse INEP.
> Fonte: Censo Escolar da Educação Básica (INEP), 2007–2024.

---

## `dim_escola.parquet`

Dimensão de escolas. Um registro por `cod_escola` (última observação disponível).

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `cod_escola` | string | Código único da escola (CO_ENTIDADE no INEP) |
| `nome_escola` | string | Nome da escola |
| `cod_regiao` | int | Código da Grande Região (1=N, 2=NE, 3=SE, 4=S, 5=CO) |
| `nome_regiao` | string | Nome da Grande Região |
| `cod_uf` | int | Código numérico da Unidade Federativa (IBGE) |
| `uf_sigla` | string | Sigla da UF (ex: SP, RJ, MG) |
| `nome_uf` | string | Nome da UF |
| `cod_municipio` | int | Código do município (IBGE 7 dígitos) |
| `nome_municipio` | string | Nome do município |
| `tp_dependencia` | int | Dependência administrativa: 1=Federal, 2=Estadual, 3=Municipal, 4=Privada |
| `desc_dependencia` | string | Descrição legível de `tp_dependencia` |
| `tp_localizacao` | int | Localização: 1=Urbana, 2=Rural |
| `desc_localizacao` | string | Descrição legível de `tp_localizacao` |
| `tp_situacao_funcionamento` | int | Situação: 1=Em atividade, 2=Paralisada, 3=Extinta no ano, 4=Extinção anterior |
| `desc_situacao` | string | Descrição legível de `tp_situacao_funcionamento` |
| `tp_categoria_escola_privada` | int | Categoria (só privadas): 1=Particular, 2=Comunitária, 3=Confessional, 4=Filantrópica, -1=Não se aplica |
| `desc_categoria_privada` | string | Descrição legível de `tp_categoria_escola_privada` |
| `in_regular` | int | 1=Oferta ensino regular, 0=Não |
| `in_eja` | int | 1=Oferta EJA, 0=Não |
| `in_especial` | int | 1=Oferta educação especial, 0=Não |
| `in_profissional` | int | 1=Oferta educação profissional, 0=Não |
| `ano_referencia` | int | Ano do último registro dessa escola no Censo |

---

## `fct_matriculas_por_escola_ano.parquet`

Fato de matrículas. Um registro por `(cod_escola, ano_censo)`.

### Chaves e dimensões

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `cod_escola` | string | Chave estrangeira → `dim_escola.cod_escola` |
| `ano_censo` | int | Ano do Censo Escolar |

### Matrículas — Total e por nível

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `qt_matriculas_total` | int | Total de matrículas na educação básica |
| `qt_mat_infantil` | int | Matrículas — Educação Infantil |
| `qt_mat_creche` | int | Matrículas — Creche (0–3 anos) |
| `qt_mat_pre_escola` | int | Matrículas — Pré-escola (4–5 anos) |
| `qt_mat_fundamental` | int | Matrículas — Ensino Fundamental |
| `qt_mat_fund_anos_iniciais` | int | Matrículas — Fundamental Anos Iniciais (1º–5º) |
| `qt_mat_fund_anos_finais` | int | Matrículas — Fundamental Anos Finais (6º–9º) |
| `qt_mat_medio` | int | Matrículas — Ensino Médio |
| `qt_mat_profissional` | int | Matrículas — Educação Profissional |
| `qt_mat_prof_tecnico` | int | Matrículas — Educação Prof. Técnica de Nível Médio |
| `qt_mat_eja` | int | Matrículas — Educação de Jovens e Adultos |
| `qt_mat_eja_fundamental` | int | Matrículas — EJA Fundamental |
| `qt_mat_eja_medio` | int | Matrículas — EJA Médio |
| `qt_mat_especial` | int | Matrículas — Educação Especial (exclusiva) |

### Matrículas — Por sexo

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `qt_mat_feminino` | int | Matrículas — sexo feminino |
| `qt_mat_masculino` | int | Matrículas — sexo masculino |

### Matrículas — Por raça/cor

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `qt_mat_branca` | int | Matrículas — cor branca |
| `qt_mat_preta` | int | Matrículas — cor preta |
| `qt_mat_parda` | int | Matrículas — cor parda |
| `qt_mat_amarela` | int | Matrículas — cor amarela |
| `qt_mat_indigena` | int | Matrículas — indígena |

---

## `fct_docentes_turmas_por_escola_ano.parquet`

Fato de docentes, turmas e infraestrutura. Um registro por `(cod_escola, ano_censo)`.

### Chaves

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `cod_escola` | string | Chave estrangeira → `dim_escola.cod_escola` |
| `ano_censo` | int | Ano do Censo Escolar |

### Docentes

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `qt_docentes_total` | int | Total de docentes |
| `qt_doc_infantil` | int | Docentes — Educação Infantil |
| `qt_doc_fundamental` | int | Docentes — Ensino Fundamental |
| `qt_doc_medio` | int | Docentes — Ensino Médio |
| `qt_doc_profissional` | int | Docentes — Educação Profissional |
| `qt_doc_eja` | int | Docentes — EJA |
| `qt_doc_especial` | int | Docentes — Educação Especial |

### Turmas

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `qt_turmas_total` | int | Total de turmas |
| `qt_tur_infantil` | int | Turmas — Educação Infantil |
| `qt_tur_fundamental` | int | Turmas — Ensino Fundamental |
| `qt_tur_medio` | int | Turmas — Ensino Médio |
| `qt_tur_eja` | int | Turmas — EJA |
| `qt_tur_especial` | int | Turmas — Educação Especial |
| `qt_salas_utilizadas` | int | Quantidade de salas de aula em uso |

### Infraestrutura (indicadores 0/1)

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `in_agua_potavel` | int | 1=Tem acesso a água potável |
| `in_energia_rede_publica` | int | 1=Tem energia elétrica pela rede pública |
| `in_internet` | int | 1=Tem acesso à internet |
| `in_internet_alunos` | int | 1=Internet disponível para os alunos |
| `in_biblioteca` | int | 1=Tem biblioteca ou sala de leitura |
| `in_laboratorio_info` | int | 1=Tem laboratório de informática |
| `in_quadra_esportes` | int | 1=Tem quadra de esportes (coberta ou descoberta) |
| `in_alimentacao` | int | 1=Oferece alimentação escolar |

---

## Valores especiais

| Valor | Significado |
|-------|-------------|
| `0` | Não / ausente (indicadores e quantidades) |
| `-1` | Tipo/categoria não informado ou não se aplica |
| `null` / `None` | Campo ausente nos dados originais do INEP para aquele ano |

---

## Cobertura temporal

| Período | Anos disponíveis |
|---------|-----------------|
| 2007–2024 | Todos os anos, **exceto 2020** (sem publicação pelo INEP) |

> **Nota sobre compatibilidade de colunas:** O INEP altera o schema dos microdados entre anos (novas colunas são adicionadas, outras descontinuadas). O pipeline lida com isso preenchendo com `0` as colunas ausentes em anos mais antigos. Consulte o relatório de inconsistências original para detalhes.
