from pathlib import Path


MARKER = "    def automatic(self, code):\n"

METHOD = '''    def _step1_enrich(self, report, code):
        """Step 1: enrich the official report with market, quarterly and core ratios."""
        try:
            today = date.today()
            row = self.price_rows.get((code, today.isoformat()), {})
            if not row:
                self.price(code, today)
                row = self.price_rows.get((code, today.isoformat()), {})

            report["market"] = {
                "close": number(row.get("clpr")),
                "volume": number(row.get("trqu")),
                "market_cap": number(row.get("mrktTotAmt")),
                "date": row.get("basDt"),
            }

            years = [int(y["year"]) for y in report.get("years", []) if y.get("year")]
            if not years:
                return report

            def amount(rows, ids=(), names=(), sj=None, field="thstrm_amount"):
                for r in rows:
                    if sj and r.get("sj_div") != sj:
                        continue
                    if r.get("account_id") in ids or r.get("account_nm") in names:
                        raw = number(r.get(field))
                        if raw is not None:
                            return raw / 100_000_000
                return None

            def statement(year, reprt):
                corp = self.corp(code)
                payload = self.dart(
                    "fnlttSinglAcntAll.json",
                    corp_code=corp,
                    bsns_year=str(year),
                    reprt_code=reprt,
                    fs_div="CFS",
                )
                return (payload or {}).get("list", [])

            quarters = []
            for year in years[-2:]:
                rev_cum = None
                op_cum = None
                for reprt, label in (("11013", "Q1"), ("11012", "Q2"), ("11014", "Q3")):
                    rows = statement(year, reprt)
                    rev = amount(rows, ["ifrs-full_Revenue"], ["매출액", "수익(매출액)"], "IS", "thstrm_add_amount")
                    op = amount(rows, ["dart_OperatingIncomeLoss"], ["영업이익", "영업이익(손실)"], "IS", "thstrm_add_amount")
                    if rev is None and op is None:
                        continue
                    qrev = rev if rev_cum is None else (None if rev is None else rev - rev_cum)
                    qop = op if op_cum is None else (None if op is None else op - op_cum)
                    quarters.append({"year": year, "quarter": label, "revenue": qrev, "operating_profit": qop})
                    if rev is not None:
                        rev_cum = rev
                    if op is not None:
                        op_cum = op

                rows = statement(year, "11011")
                annual_rev = amount(rows, ["ifrs-full_Revenue"], ["매출액", "수익(매출액)"], "IS")
                annual_op = amount(rows, ["dart_OperatingIncomeLoss"], ["영업이익", "영업이익(손실)"], "IS")
                quarters.append({
                    "year": year,
                    "quarter": "Q4",
                    "revenue": None if annual_rev is None or rev_cum is None else annual_rev - rev_cum,
                    "operating_profit": None if annual_op is None or op_cum is None else annual_op - op_cum,
                })
            report["quarters"] = quarters[-8:]

            enriched = []
            for item in report.get("years", []):
                year = int(item["year"])
                rows = statement(year, "11011")
                revenue = amount(rows, ["ifrs-full_Revenue"], ["매출액", "수익(매출액)"], "IS")
                op = amount(rows, ["dart_OperatingIncomeLoss"], ["영업이익", "영업이익(손실)"], "IS")
                net = amount(
                    rows,
                    ["ifrs-full_ProfitLossAttributableToOwnersOfParent"],
                    ["지배기업의 소유주에게 귀속되는 당기순이익(손실)"],
                    "IS",
                )
                equity = amount(rows, ["ifrs-full_Equity"], ["자본", "자본총계"], "BS")
                liabilities = amount(rows, ["ifrs-full_Liabilities"], ["부채", "부채총계"], "BS")
                cfo = amount(rows, ["ifrs-full_CashFlowsFromUsedInOperatingActivities"], ["영업활동으로 인한 현금흐름"], "CF")
                capex = amount(rows, ["ifrs-full_PurchaseOfPropertyPlantAndEquipment"], ["유형자산의 취득"], "CF")
                enriched.append({
                    **item,
                    "revenue": revenue if revenue is not None else item.get("revenue"),
                    "profit": op if op is not None else item.get("profit"),
                    "net_income": net if net is not None else item.get("net_income"),
                    "equity": equity,
                    "liabilities": liabilities,
                    "cfo": cfo,
                    "capex": capex,
                    "fcf": None if cfo is None or capex is None else cfo - abs(capex),
                    "operating_margin": None if not revenue or op is None else op / revenue * 100,
                    "roe": None if not equity or net is None else net / equity * 100,
                    "debt_ratio": None if not equity or liabilities is None else liabilities / equity * 100,
                    "eps": item.get("eps"),
                })
            report["years"] = enriched
            return report
        except DataError:
            return report

'''


def main():
    path = Path("providers.py")
    source = path.read_text(encoding="utf-8")
    if "def _step1_enrich" in source:
        return
    if MARKER not in source:
        raise SystemExit("providers.py: automatic() marker not found")
    source = source.replace(MARKER, METHOD + MARKER, 1)
    source = source.replace(
        "            return self._automatic_direct(code)\n",
        "            return self._step1_enrich(self._automatic_direct(code), code)\n",
        1,
    )
    path.write_text(source, encoding="utf-8")


if __name__ == "__main__":
    main()
