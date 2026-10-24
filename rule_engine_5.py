import csv


def ingest(path, is_train):
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            if is_train == (row["trans_date_trans_time"] < "2020-01-01"):
                yield row


rulesets = [
    {
        "id": "2",
        "name": "Amount fingerprint",
        "combinator": "AND",
        "conditions": [
            {
                "field": "category",
                "operator": "==",
                "value": "grocery_pos",
                "type": "single",
            },
            {
                "type": "composite",
                "combinator": "AND",
                "conditions": [
                    {
                        "type": "single",
                        "field": "amt",
                        "operator": ">",
                        "value": "269.99",
                    },
                    {
                        "type": "single",
                        "field": "amt",
                        "operator": "<",
                        "value": "380.01",
                    },
                ],
            },
        ],
        "type": "composite",
        "action": "SendAlert",
    },
]


from decimal import Decimal
from collections import defaultdict
from typing import Callable


class RuleEngine:
    def build_predicate(self, conditions, combinator) -> Callable[[dict], bool]:
        fns = []

        for condition in conditions:
            if condition["type"] == "composite":
                fn = self.build_predicate(condition["conditions"], condition["combinator"])
                fns.append(fn)
                continue

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


from anthropic import AsyncAnthropic
import os
from dotenv import load_dotenv

load_dotenv()


async def analyze_with_llm(dataset):
    print("analyzing")
    client = AsyncAnthropic(
        api_key=os.environ.get(
            "ANTHROPIC_API_KEY"
        ),  # This is the default and can be omitted
    )
    text = f"""
    You are a financial analyst.
    Here is a dataset from csv with credit card fraud (is_fraud = 1)

    Find 2-3 patterns or reasons in this list.

    Dataset:
    {dataset}
    """
    async with client.messages.stream(
        max_tokens=128000,
        messages=[
            {
                "content": text,
                "role": "user",
            }
        ],
        model="claude-opus-5-5",
    ) as stream:
        with open("output/output.md", "w") as f:
            async for text in stream.text_stream:
                f.write(text)

            message = await stream.get_final_message()
            print(message.to_json())


import asyncio


def main() -> None:
    rule_engine = RuleEngine(rulesets)

    train = ingest("/Users/yichizhang/data/kaggle/credit_card_transactions.csv", True)
    verify = ingest("/Users/yichizhang/data/kaggle/credit_card_transactions.csv", False)

    res = rule_engine.execute(train)

    dataset_ids = {}

    for rulename, transactions in res.items():
        dataset_ids[rulename] = [
            transaction["Unnamed: 0"] for transaction in transactions
        ]

    # failure_ids = {
    #     rulename: [transaction["id"] for transaction in transactions]
    #     for rulename, transactions in rule_engine.failures.items()
    # }
    # asyncio.run(analyze_with_llm(res["Is Fraud"][:1000]))
    print(len(res["Amount fingerprint"]))

    fingerprint = res["Amount fingerprint"]
    assert all(row["category"] == "grocery_pos" for row in fingerprint)
    assert all(
        Decimal("269.99") < Decimal(row["amt"]) < Decimal("380.01") for row in fingerprint
    )


if __name__ == "__main__":
    main()
