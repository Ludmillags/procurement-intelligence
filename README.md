# Procurement Intelligence

Sistema de apoio à decisão em Compras e Suprimentos com análise de dados.

![Python](https://img.shields.io/badge/Python-Data%20Analytics-3776AB?logo=python&logoColor=white) ![Pandas](https://img.shields.io/badge/Pandas-ETL%20%26%20Analytics-150458?logo=pandas&logoColor=white) ![Excel](https://img.shields.io/badge/Excel-Import%20%26%20Export-217346?logo=microsoftexcel&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-Web%20App-F7DF1E?logo=javascript&logoColor=111)

> **Case de portfólio:** os dados demonstrativos são sintéticos e foram criados exclusivamente para estudo e apresentação profissional.

## Visão geral

O **Procurement Intelligence** nasceu de um problema comum da rotina de suprimentos: a equalização de propostas exige consultar histórico de preços, impostos, frete, prazo, atrasos, qualidade e condições comerciais antes de decidir de quem comprar.

A aplicação reúne essas informações em uma única análise e cria um **Best Buy Score**, evitando que a decisão seja tomada apenas pelo menor preço.

## Problema → Solução → Resultado

| Etapa | Descrição |
|---|---|
| **Problema** | Equalização manual, consulta demorada ao último preço e pouca visibilidade sobre risco de fornecedores. |
| **Solução** | Importação da base histórica e da cotação em Excel, cálculo automático de indicadores e score multicritério. |
| **Resultado** | Comparação estruturada entre fornecedores, alertas de risco e recomendação baseada em custo + desempenho. |

## Funcionalidades

- Importação da base histórica e cotação em Excel
- Validação e limpeza de dados
- Equalização de propostas
- Último preço e média histórica de 12 meses
- OTD e atraso médio
- Indicador de qualidade
- Custo total com imposto e frete
- Ranking de fornecedores e alertas
- **Best Buy Score** configurável
- Recomendação de fornecedor
- Exportação para Excel
- Pipeline Python comentado para estudo

## Best Buy Score

| Critério | Peso |
|---|---:|
| Preço | 35% |
| Pontualidade / OTD | 30% |
| Lead Time | 15% |
| Qualidade | 10% |
| Prazo de pagamento | 10% |

O menor preço não vence automaticamente se o fornecedor apresentar maior risco operacional.

## Tecnologias

**Web:** HTML5 · CSS3 · JavaScript · SVG · Excel  
**Analytics:** Python · Pandas · OpenPyXL

## Para recrutadores

Este projeto demonstra a combinação de **conhecimento de negócio em suprimentos** com competências técnicas em análise de dados, automação, KPI Design e regras de negócio.

> Desenvolvi uma solução para automatizar a equalização de propostas em suprimentos. O sistema cruza a cotação atual com o histórico de compras e a performance dos fornecedores, calcula indicadores como último preço, média histórica, OTD, atraso, qualidade e custo total e utiliza um modelo multicritério para recomendar a alternativa com melhor relação entre custo e risco operacional.

## Roadmap

- [x] Interface web
- [x] Importação de Excel
- [x] Equalização automática
- [x] Supplier Performance
- [x] Price Intelligence
- [x] Best Buy Score
- [x] Alertas e exportação
- [x] Pipeline Python comentado
- [ ] PostgreSQL
- [ ] API com FastAPI
- [ ] Power BI
- [ ] Login e perfis de acesso
- [ ] Integração com ERP
- [ ] Testes automatizados

## Autoria

Projeto criado como case de **Data Analytics aplicado a Procurement / Supply Chain** por Ludmilla G. Costa.