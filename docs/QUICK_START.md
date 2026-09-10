# Quick Start

## Aplicação Web

1. Abra `index.html`.
2. Clique em **Importar Base de Compras**.
3. Selecione um arquivo `.xlsx`.
4. Clique em **Importar Cotação**.
5. Selecione a cotação `.xlsx`.
6. Clique em **Analisar Compra**.

## Python

```bash
pip install -r requirements.txt
python python/procurement_analysis.py --base base_compras.xlsx --cotacao cotacao.xlsx --saida relatorio_procurement.xlsx
```

## Base Histórica — campos mínimos

- `data_pedido`
- `id_material`
- `preco_unitario`
- `id_fornecedor`

## Cotação — campos mínimos

- `id_material`
- `id_fornecedor`
- `preco_cotado`
- `quantidade`
- `aliquota_imposto`
- `frete`
- `prazo_entrega_dias`
- `prazo_pagamento_dias`
