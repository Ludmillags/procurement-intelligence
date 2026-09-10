"""Procurement Intelligence — pipeline didático de análise de compras.

Instalação:
    pip install -r requirements.txt

Uso:
    python python/procurement_analysis.py --base base.xlsx --cotacao cotacao.xlsx --saida relatorio.xlsx
"""
from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

WEIGHTS = {"price": .35, "punctuality": .30, "lead_time": .15, "quality": .10, "payment": .10}
PRICE_ALERT = .10
DELAY_CRITICAL = 7
QUALITY_MIN = .90


def read_excel_file(path: Path) -> pd.DataFrame:
    """Lê a primeira aba e padroniza os nomes das colunas."""
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")
    df = pd.read_excel(path)
    df.columns = df.columns.astype(str).str.strip().str.lower().str.replace(" ", "_", regex=False)
    return df


def validate_columns(df: pd.DataFrame, required: list[str], name: str) -> None:
    """Evita que uma planilha incompleta siga para os cálculos."""
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"{name}: colunas obrigatórias ausentes: {', '.join(missing)}")


def build_price_history(base: pd.DataFrame) -> pd.DataFrame:
    """Calcula último preço e média dos últimos 12 meses por material."""
    work = base.copy()
    work["data_pedido"] = pd.to_datetime(work["data_pedido"], errors="coerce")
    work["preco_unitario"] = pd.to_numeric(work["preco_unitario"], errors="coerce")
    work = work.dropna(subset=["data_pedido", "id_material", "preco_unitario"]).sort_values(["id_material", "data_pedido"])
    last = work.groupby("id_material", as_index=False).tail(1)[["id_material", "preco_unitario"]].rename(columns={"preco_unitario": "ultimo_preco"})
    cutoff = work["data_pedido"].max() - pd.DateOffset(months=12)
    avg = work[work["data_pedido"] >= cutoff].groupby("id_material", as_index=False)["preco_unitario"].mean().rename(columns={"preco_unitario": "media_preco_12m"})
    return last.merge(avg, on="id_material", how="left")


def build_supplier_performance(base: pd.DataFrame) -> pd.DataFrame:
    """Cria atraso médio, OTD e qualidade por fornecedor."""
    work = base.copy()
    if "atraso_dias" in work:
        work["atraso_dias"] = pd.to_numeric(work["atraso_dias"], errors="coerce").fillna(0)
    elif {"data_prometida", "data_entrega"}.issubset(work.columns):
        promised = pd.to_datetime(work["data_prometida"], errors="coerce")
        delivered = pd.to_datetime(work["data_entrega"], errors="coerce")
        work["atraso_dias"] = (delivered - promised).dt.days.clip(lower=0).fillna(0)
    else:
        work["atraso_dias"] = 0

    if "status_prazo" in work:
        work["on_time"] = work["status_prazo"].astype(str).str.strip().str.lower().eq("no prazo").astype(float)
    else:
        work["on_time"] = (work["atraso_dias"] <= 0).astype(float)

    if "status_qualidade" in work:
        work["quality_ok"] = work["status_qualidade"].astype(str).str.strip().str.lower().eq("conforme").astype(float)
    else:
        work["quality_ok"] = .95

    return work.groupby("id_fornecedor", as_index=False).agg(
        atraso_medio_dias=("atraso_dias", "mean"), otd=("on_time", "mean"),
        qualidade=("quality_ok", "mean"), total_compras=("id_fornecedor", "size"))


def clamp(value: float) -> float:
    return max(0, min(100, value))


def score(row: pd.Series) -> pd.Series:
    """Transforma critérios diferentes em uma escala comparável de 0 a 100."""
    price = clamp(100 - max(row["variacao_vs_media_12m"], 0) * 250)
    punctuality = clamp(row["otd"] * 100)
    lead = clamp(100 - row["prazo_entrega_dias"] * 3)
    quality = clamp(row["qualidade"] * 100)
    payment = clamp(row["prazo_pagamento_dias"] / 60 * 100)
    best = price*WEIGHTS["price"] + punctuality*WEIGHTS["punctuality"] + lead*WEIGHTS["lead_time"] + quality*WEIGHTS["quality"] + payment*WEIGHTS["payment"]
    return pd.Series({"score_preco": price, "score_pontualidade": punctuality, "score_lead_time": lead, "score_qualidade": quality, "score_pagamento": payment, "best_buy_score": best})


def analyze(base: pd.DataFrame, quotes: pd.DataFrame):
    """Cruza histórico e cotação, calcula KPIs, alertas e recomendação."""
    validate_columns(base, ["data_pedido", "id_material", "preco_unitario", "id_fornecedor"], "Base de compras")
    required = ["id_material", "id_fornecedor", "preco_cotado", "quantidade", "aliquota_imposto", "frete", "prazo_entrega_dias", "prazo_pagamento_dias"]
    validate_columns(quotes, required, "Cotação")

    result = quotes.copy()
    for col in ["preco_cotado", "quantidade", "aliquota_imposto", "frete", "prazo_entrega_dias", "prazo_pagamento_dias"]:
        result[col] = pd.to_numeric(result[col], errors="coerce").fillna(0)

    result = result.merge(build_price_history(base), on="id_material", how="left").merge(build_supplier_performance(base), on="id_fornecedor", how="left")
    result["ultimo_preco"] = result["ultimo_preco"].fillna(result["preco_cotado"])
    result["media_preco_12m"] = result["media_preco_12m"].fillna(result["ultimo_preco"])
    result["atraso_medio_dias"] = result["atraso_medio_dias"].fillna(0)
    result["otd"] = result["otd"].fillna(.80)
    result["qualidade"] = result["qualidade"].fillna(.95)
    result["custo_total"] = result["quantidade"] * result["preco_cotado"] * (1 + result["aliquota_imposto"]) + result["frete"]
    result["variacao_vs_ultimo"] = result["preco_cotado"] / result["ultimo_preco"] - 1
    result["variacao_vs_media_12m"] = result["preco_cotado"] / result["media_preco_12m"] - 1
    result = pd.concat([result, result.apply(score, axis=1)], axis=1)

    def alert(r):
        alerts = []
        if r["variacao_vs_media_12m"] > PRICE_ALERT: alerts.append("PREÇO ACIMA DA MÉDIA")
        if r["atraso_medio_dias"] > DELAY_CRITICAL: alerts.append("ATRASO CRÍTICO")
        if r["qualidade"] < QUALITY_MIN: alerts.append("QUALIDADE ABAIXO DO LIMITE")
        return " | ".join(alerts) if alerts else "OK"

    result["alerta"] = result.apply(alert, axis=1)
    result["recomendado"] = False
    winners = result.groupby("id_material")["best_buy_score"].idxmax().dropna().astype(int)
    result.loc[winners, "recomendado"] = True
    recommendations = result[result["recomendado"]].copy()
    return result.sort_values(["id_material", "best_buy_score"], ascending=[True, False]), recommendations


def export_report(equalization: pd.DataFrame, recommendations: pd.DataFrame, output: Path) -> None:
    """Gera um workbook com equalização completa e recomendações."""
    output.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        equalization.to_excel(writer, sheet_name="Equalizacao", index=False)
        recommendations.to_excel(writer, sheet_name="Recomendacoes", index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Procurement Intelligence")
    parser.add_argument("--base", required=True, type=Path)
    parser.add_argument("--cotacao", required=True, type=Path)
    parser.add_argument("--saida", type=Path, default=Path("relatorio_procurement.xlsx"))
    args = parser.parse_args()
    print("Lendo arquivos...")
    equalization, recommendations = analyze(read_excel_file(args.base), read_excel_file(args.cotacao))
    export_report(equalization, recommendations, args.saida)
    print(f"Concluído: {len(equalization)} propostas | {equalization['id_material'].nunique()} materiais")
    print(f"Relatório: {args.saida.resolve()}")


if __name__ == "__main__":
    main()
