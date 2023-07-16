# PyTD

API Python para Tesouro Direto

Esse projeto ainda está em fase de testes.
Por enquanto, ele apenas baixa uma lista dos títulos do TD que você tem, cada um em formato JSON.


## Configuração

Faça a instalação dos módulos `bs4`, `python-dotenv` e `requests`

```
pip install bs4 python-dotenv requests
```

Crie um arquivo `.env` com o seguinte conteúdo:

```
CPF=<seu CPF, somente os números>
SENHA=<senha no Tesouro Direto>
```

