from collections import defaultdict
from typing import Callable, Iterator

_rulesets = [
    {
        "id": "1",
        "name": "High_Value_Band",
        "combinator": "AND",
        "conditions": [
            {"field": "amount", "operator": ">", "value": "14000"},
            {"field": "amount", "operator": "<", "value": "16000"},
        ],
        "action": "SendAlert",
    },
    {
        "id": "2",
        "name": "Small_Positive",
        "combinator": "AND",
        "conditions": [
            {"field": "amount", "operator": ">", "value": "0"},
            {"field": "amount", "operator": "<", "value": "100"},
        ],
        "action": "FlagReview",
    },
    {
        "id": "3",
        "name": "Zero_or_Above_16000",
        "combinator": "OR",
        "conditions": [
            {"field": "amount", "operator": "==", "value": "0"},
            {"field": "amount", "operator": ">", "value": "16000"},
        ],
        "action": "Escalate",
    },
    {
        "id": "4",
        "name": "USD_or_EUR",
        "combinator": "OR",
        "conditions": [
            {"field": "currency", "operator": "==", "value": "USD"},
            {"field": "currency", "operator": "==", "value": "EUR"},
        ],
        "action": "Log",
    },
    {
        "id": "5",
        "name": "Large_USD",
        "combinator": "AND",
        "conditions": [
            {"field": "currency", "operator": "==", "value": "USD"},
            {"field": "amount", "operator": ">", "value": "10000"},
        ],
        "action": "HoldUSD",
    },
    {
        "id": "6",
        "name": "Euro",
        "combinator": "AND",
        "conditions": [
            {"field": "currency", "operator": "==", "value": "EUR"},
        ],
        "action": "HoldEUR",
    },
    {
        "id": "7",
        "name": "Exact_Threshold",
        "combinator": "OR",
        "conditions": [
            {"field": "amount", "operator": "==", "value": "14000"},
            {"field": "amount", "operator": "==", "value": "16000"},
            {"field": "amount", "operator": "==", "value": "10000"},
        ],
        "action": "SendAlert",
    },
    {
        "id": "8",
        "name": "Negative_USD",
        "combinator": "AND",
        "conditions": [
            {"field": "currency", "operator": "==", "value": "USD"},
            {"field": "amount", "operator": "<", "value": "0"},
        ],
        "action": "Escalate",
    },
    {
        "id": "9",
        "name": "Large_Refund",
        "combinator": "AND",
        "conditions": [
            {"field": "amount", "operator": "<", "value": "-10000"},
        ],
        "action": "Escalate",
    },
    {
        "id": "10",
        "name": "Lowercase_Currency",
        "combinator": "OR",
        "conditions": [
            {"field": "currency", "operator": "==", "value": "usd"},
            {"field": "currency", "operator": "==", "value": "eur"},
            {"field": "currency", "operator": "==", "value": "yuan"},
            {"field": "currency", "operator": "==", "value": "cad"},
        ],
        "action": "FlagReview",
    },
    {
        "id": "11",
        "name": "Padded_Currency",
        "combinator": "OR",
        "conditions": [
            {"field": "currency", "operator": "==", "value": "USD "},
            {"field": "currency", "operator": "==", "value": "EUR "},
            {"field": "currency", "operator": "==", "value": "CAD "},
            {"field": "currency", "operator": "==", "value": "YUAN "},
        ],
        "action": "FlagReview",
    },
    {
        "id": "12",
        "name": "None_Sentinel",
        "combinator": "OR",
        "conditions": [
            {"field": "amount", "operator": "==", "value": "None"},
            {"field": "currency", "operator": "==", "value": "None"},
        ],
        "action": "Reject",
    },
    {
        "id": "13",
        "name": "Swapped_Amount",
        "combinator": "OR",
        "conditions": [
            {"field": "amount", "operator": "==", "value": "USD"},
            {"field": "amount", "operator": "==", "value": "EUR"},
            {"field": "amount", "operator": "==", "value": "CAD"},
            {"field": "amount", "operator": "==", "value": "YUAN"},
        ],
        "action": "Reject",
    },
    {
        "id": "14",
        "name": "Flagged_Duplicate",
        "combinator": "AND",
        "conditions": [
            {"field": "note", "operator": "==", "value": "dup"},
            {"field": "flagged", "operator": "==", "value": "True"},
        ],
        "action": "Hold",
    },
    {
        "id": "15",
        "name": "Manual_or_Review",
        "combinator": "OR",
        "conditions": [
            {"field": "note", "operator": "==", "value": "manual"},
            {"field": "note", "operator": "==", "value": "review"},
        ],
        "action": "FlagReview",
    },
    {
        "id": "16",
        "name": "Unflagged_Review",
        "combinator": "AND",
        "conditions": [
            {"field": "note", "operator": "==", "value": "review"},
            {"field": "flagged", "operator": "==", "value": "False"},
        ],
        "action": "Log",
    },
    {
        "id": "17",
        "name": "Blank_Amount",
        "combinator": "AND",
        "conditions": [
            {"field": "amount", "operator": "==", "value": ""},
        ],
        "action": "FlagReview",
    },
    {
        "id": "18",
        "name": "Zero_Yuan",
        "combinator": "AND",
        "conditions": [
            {"field": "amount", "operator": "==", "value": "0"},
            {"field": "currency", "operator": "==", "value": "YUAN"},
        ],
        "action": "Reject",
    },
    {
        "id": "19",
        "name": "Decimal_Zero",
        "combinator": "AND",
        "conditions": [
            {"field": "amount", "operator": "==", "value": "0.0"},
        ],
        "action": "Escalate",
    },
    {
        "id": "20",
        "name": "Title_Case_Currency",
        "combinator": "OR",
        "conditions": [
            {"field": "currency", "operator": "==", "value": "Usd"},
            {"field": "currency", "operator": "==", "value": "Eur"},
            {"field": "currency", "operator": "==", "value": "Yuan"},
            {"field": "currency", "operator": "==", "value": "Cad"},
        ],
        "action": "Log",
    },
    {
        "id": "21",
        "name": "Blank_Currency",
        "combinator": "AND",
        "conditions": [
            {"field": "currency", "operator": "==", "value": ""},
        ],
        "action": "FlagReview",
    },
]

class RuleEngine:
    def build_predicate(self, conditions, combinator) -> Callable[[dict], bool]:
        fns = []
        for condition in conditions:
            if condition["operator"] == ">":
                fn = lambda x, field=condition["field"], value=condition["value"]: (
                    Decimal(x[field]) > Decimal(value)
                )
                fns.append(fn)
            elif condition["operator"] == "<":
                fn = lambda x, field=condition["field"], value=condition["value"]: (
                    Decimal(x[field]) < Decimal(value)
                )
                fns.append(fn)
            elif condition["operator"] == "==":
                fn = lambda x, field=condition["field"], value=condition["value"]: (
                    x[field] == value
                )
                fns.append(fn)

        if combinator == "AND":
            return lambda x: all(fn(x) for fn in fns)
        if combinator == "OR":
            return lambda x: any(fn(x) for fn in fns)

    def __init__(self, rulesets):
        self.rulesFncs = defaultdict(list)

        for ruleset in rulesets:
            self.rulesFncs[ruleset["name"]] = {
                "conditions": self.build_predicate(ruleset["conditions"], ruleset["combinator"])
            }

    def execute(self, dataset):
        self.res = defaultdict(list)
        self.failures = defaultdict(list)

        for data in dataset:
            for rule_name, rules in self.rulesFncs.items():
                fn = rules["conditions"]
                try:
                    if fn(data):
                        self.res[rule_name].append(data)
                except:
                    self.failures[rule_name].append(data)

        return self.res

from decimal import Decimal
import csv

def ingest(path) -> Iterator:
    with open(path, newline="") as f:
        yield from csv.DictReader(f)


def check(dataset_ids, failure_ids) -> None:
    matched = {name: set(ids) for name, ids in dataset_ids.items()}
    failed = {name: set(ids) for name, ids in failure_ids.items()}

    # 19: blank amount and blank currency
    assert "19" in failed.get("High_Value_Band", ())
    assert "19" in matched.get("Blank_Amount", ())
    assert "19" in matched.get("Blank_Currency", ())

    # 6: blank amount, currency CAD
    assert "6" in failed.get("High_Value_Band", ())
    assert "6" in matched.get("Blank_Amount", ())
    assert "6" not in failed.get("Blank_Amount", ())

    # 11: amount 0, blank currency. "0" is not "0.0"
    assert "11" in matched.get("Zero_or_Above_16000", ())
    assert "11" not in failed.get("Zero_or_Above_16000", ())
    assert "11" in matched.get("Blank_Currency", ())
    assert "11" not in matched.get("Decimal_Zero", ())

    # 3: amount 0, currency EUR
    assert "3" in matched.get("Zero_or_Above_16000", ())
    assert "3" in matched.get("Euro", ())
    assert "3" not in matched.get("Decimal_Zero", ())

    # 1: 0 YUAN, note dup, flagged True
    assert "1" in matched.get("Zero_Yuan", ())
    assert "1" in matched.get("Flagged_Duplicate", ())

    # 2: 233190, blank currency
    assert "2" in matched.get("Zero_or_Above_16000", ())
    assert "2" in matched.get("Blank_Currency", ())
    assert "2" not in matched.get("High_Value_Band", ())

    # 16: 15000, blank currency
    assert "16" in matched.get("High_Value_Band", ())
    assert "16" in matched.get("Blank_Currency", ())
    assert "16" not in matched.get("USD_or_EUR", ())

    # 27: 99, blank currency
    assert "27" in matched.get("Small_Positive", ())
    assert "27" in matched.get("Blank_Currency", ())
    assert "27" not in matched.get("Zero_or_Above_16000", ())

    # 47: 100 USD. 100 is not below 100, and not above 10000
    assert "47" not in matched.get("Small_Positive", ())
    assert "47" in matched.get("USD_or_EUR", ())
    assert "47" not in matched.get("Large_USD", ())
    assert "47" not in matched.get("Exact_Threshold", ())

    # 193: 1 usd
    assert "193" in matched.get("Small_Positive", ())
    assert "193" in matched.get("Lowercase_Currency", ())
    assert "193" not in matched.get("USD_or_EUR", ())

    # 7: 14001 USD
    assert "7" in matched.get("High_Value_Band", ())
    assert "7" in matched.get("Large_USD", ())
    assert "7" not in matched.get("Exact_Threshold", ())

    # 4: 14001 YUAN, note manual, flagged True
    assert "4" in matched.get("High_Value_Band", ())
    assert "4" in matched.get("Manual_or_Review", ())
    assert "4" not in matched.get("Flagged_Duplicate", ())

    # 141 and 234: amount exactly 14000
    assert "141" in matched.get("Exact_Threshold", ())
    assert "141" not in matched.get("High_Value_Band", ())
    assert "141" in matched.get("Large_USD", ())
    assert "234" in matched.get("Exact_Threshold", ())
    assert "234" in matched.get("Manual_or_Review", ())
    assert "234" not in matched.get("Unflagged_Review", ())
    assert "234" not in matched.get("Flagged_Duplicate", ())
    assert "234" not in matched.get("High_Value_Band", ())

    # 30: 16000 CAD. 87: 10000 CAD. 32: 16000 EUR
    assert "30" not in matched.get("High_Value_Band", ())
    assert "30" not in matched.get("Zero_or_Above_16000", ())
    assert "30" in matched.get("Exact_Threshold", ())
    assert "87" in matched.get("Exact_Threshold", ())
    assert "87" not in matched.get("USD_or_EUR", ())
    assert "87" not in matched.get("Large_USD", ())
    assert "32" in matched.get("Exact_Threshold", ())
    assert "32" in matched.get("Euro", ())
    assert "32" not in matched.get("Zero_or_Above_16000", ())

    # 33: 16001 EUR, note dup, flagged True
    assert "33" in matched.get("Flagged_Duplicate", ())
    assert "33" in matched.get("Euro", ())
    assert "33" in matched.get("Zero_or_Above_16000", ())
    assert "33" not in matched.get("Exact_Threshold", ())

    # 80: 0.0 EUR. "0.0" is not "0"
    assert "80" not in matched.get("Zero_or_Above_16000", ())
    assert "80" in matched.get("Decimal_Zero", ())
    assert "80" in matched.get("Euro", ())
    assert "80" not in failed.get("High_Value_Band", ())

    # 8: 67740, currency text None
    assert "8" not in matched.get("USD_or_EUR", ())
    assert "8" not in failed.get("USD_or_EUR", ())
    assert "8" in matched.get("None_Sentinel", ())
    assert "8" in matched.get("Zero_or_Above_16000", ())

    # 49: amount text None, currency USD
    assert "49" in failed.get("Large_USD", ())
    assert "49" in matched.get("USD_or_EUR", ())
    assert "49" in matched.get("None_Sentinel", ())

    # 13: amount EUR, currency 107332. 75: amount USD, currency 14000
    assert "13" in failed.get("High_Value_Band", ())
    assert "13" in matched.get("Swapped_Amount", ())
    assert "75" in failed.get("High_Value_Band", ())
    assert "75" not in matched.get("High_Value_Band", ())
    assert "75" in matched.get("Swapped_Amount", ())

    # 17: 113632, currency "YUAN "
    assert "17" not in matched.get("Zero_Yuan", ())
    assert "17" in matched.get("Padded_Currency", ())

    # 169: 100, currency "USD "
    assert "169" in matched.get("Padded_Currency", ())
    assert "169" not in matched.get("USD_or_EUR", ())
    assert "169" not in matched.get("Small_Positive", ())

    # 142: 15999 cad
    assert "142" in matched.get("High_Value_Band", ())
    assert "142" not in matched.get("USD_or_EUR", ())
    assert "142" in matched.get("Lowercase_Currency", ())

    # 118: 2620 Yuan
    assert "118" in matched.get("Title_Case_Currency", ())
    assert "118" not in matched.get("Lowercase_Currency", ())
    assert "118" not in matched.get("Zero_Yuan", ())

    # 55: 16001 Eur. 40 is title case too
    assert "40" in matched.get("Title_Case_Currency", ())
    assert "55" in matched.get("Title_Case_Currency", ())
    assert "55" not in matched.get("Euro", ())
    assert "55" not in matched.get("Exact_Threshold", ())

    # 220: -16660 USD. 444: -2287 USD. 59: -35322 CAD. 103: -8085 CAD. 100: -14774 EUR
    assert "220" in matched.get("Negative_USD", ())
    assert "220" in matched.get("Large_Refund", ())
    assert "220" not in failed.get("Negative_USD", ())
    assert "220" in matched.get("USD_or_EUR", ())
    assert "444" in matched.get("Negative_USD", ())
    assert "444" not in matched.get("Large_Refund", ())
    assert "59" in matched.get("Large_Refund", ())
    assert "59" not in matched.get("Negative_USD", ())
    assert "103" not in matched.get("Large_Refund", ())
    assert "103" not in matched.get("Negative_USD", ())
    assert "100" in matched.get("Large_Refund", ())
    assert "100" in matched.get("Euro", ())
    assert "100" not in matched.get("Negative_USD", ())

    # 189: 90804 USD, note review, flagged False. 143: review, flagged True
    assert "189" in matched.get("Unflagged_Review", ())
    assert "189" in matched.get("Manual_or_Review", ())
    assert "189" not in matched.get("Flagged_Duplicate", ())
    assert "143" in matched.get("Manual_or_Review", ())
    assert "143" not in matched.get("Unflagged_Review", ())
    assert "143" not in matched.get("Flagged_Duplicate", ())

    # 4660: 15621.52 USD
    assert "4660" in matched.get("High_Value_Band", ())
    assert "4660" in matched.get("Large_USD", ())


def main() -> None:
    rule_engine = RuleEngine(_rulesets)

    dataset = ingest("transactions.csv")

    res = rule_engine.execute(dataset)

    dataset_ids = {}

    for rulename, transactions in res.items():
        dataset_ids[rulename] = [transaction["id"] for transaction in transactions]

    failure_ids = {
        rulename: [transaction["id"] for transaction in transactions]
        for rulename, transactions in rule_engine.failures.items()
    }
    check(dataset_ids, failure_ids)


if __name__ == "__main__":
    main()
