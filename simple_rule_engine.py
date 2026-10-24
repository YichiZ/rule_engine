from collections import defaultdict

_dataset = [
    {"id": "1", "amount": 15000, "currency": "USD"},
    {"id": "2", "amount": 10001, "currency": "USD"},
    {"id": "3", "amount": 10000, "currency": "USD"},
    {"id": "4", "amount": 15000, "currency": "EUR"},
    {"id": "5", "amount": 100, "currency": "USD"},
    {"id": "6", "amount": 99, "currency": "EUR"},
    {"id": "7", "amount": 50, "currency": "USD"},
    {"id": "8", "amount": 0, "currency": "USD"},
    {"id": "9", "amount": 20000, "currency": "EUR"},
]

_rulesets = [
    {
        "id": "1",
        "name": "High_Value_Transaction",
        "conditions": [
            {"field": "amount", "operator": ">", "value": 14000},
            {"field": "amount", "operator": "<", "value": 16000},
        ],
        "action": "SendAlert",
    },
    {
        "id": "2",
        "name": "Small_Transaction",
        "conditions": [
            {"field": "amount", "operator": ">", "value": 0},
            {"field": "amount", "operator": "<", "value": 100},
        ],
        "action": "FlagReview",
    },
    {
        "id": "3",
        "name": "Zero_Amount",
        "conditions": [
            {"field": "amount", "operator": "==", "value": 0},
        ],
        "action": "Reject",
    },
    {
        "id": "4",
        "name": "Very_High_Value",
        "conditions": [
            {"field": "amount", "operator": ">", "value": 16000},
        ],
        "action": "Escalate",
    },
    {
        "id": "5",
        "name": "USD_Transaction",
        "conditions": [
            {"field": "currency", "operator": "==", "value": "USD"},
        ],
        "action": "LogUSD",
    },
    {
        "id": "6",
        "name": "USD_Transaction_Over_10000",
        "conditions": [
            {"field": "currency", "operator": "==", "value": "USD"},
            {"field": "amount", "operator": ">", "value": 10000},
        ],
        "action": "HoldUSD",
    },
    {
        "id": "7",
        "name": "euro_transaction",
        "conditions": [
            {"field": "currency", "operator": "==", "value": "EUR"},
        ],
        "action": "HoldUSD",
    },
]

from collections import defaultdict

class RuleEngine:
    def add_conditions(self, conditions) -> list:
        fns = []
        for condition in conditions:
            if condition["operator"] == ">":
                fn = lambda x, field=condition["field"], value=condition["value"]: (
                    x[field] > value
                )
                fns.append(fn)
            elif condition["operator"] == "<":
                fn = lambda x, field=condition["field"], value=condition["value"]: (
                    x[field] < value
                )
                fns.append(fn)
            elif condition["operator"] == "==":
                fn = lambda x, field=condition["field"], value=condition["value"]: (
                    x[field] == value
                )
                fns.append(fn)
        return fns

    def __init__(self, rulesets):
        self.rulesFncs = defaultdict(list)

        for ruleset in rulesets:
            conditions = ruleset["conditions"]
            self.rulesFncs[ruleset["name"]] = self.add_conditions(conditions)

    def execute(self, dataset):
        res = {}
        for rule_name, rules in self.rulesFncs.items():
            result = []
            for data in dataset:
                fns = [rule(data) for rule in rules]
                if all(fns):
                    result.append(data)
            res[rule_name] = result

        return res


def main() -> None:
    rule_engine = RuleEngine(_rulesets)
    res = rule_engine.execute(_dataset)

    dataset_ids = {}
    
    for rulename, transactions in res.items():
        dataset_ids[rulename] = [transaction["id"] for transaction in transactions]
    
    assert set(dataset_ids["High_Value_Transaction"]) == {"1", "4"}
    assert set(dataset_ids["Small_Transaction"]) == {"6", "7"}
    assert set(dataset_ids["Zero_Amount"]) == {"8"}
    assert set(dataset_ids["Very_High_Value"]) == {"9"}
    assert set(dataset_ids["USD_Transaction"]) == {"1", "2", "3", "5", "7", "8"}
    assert set(dataset_ids["USD_Transaction_Over_10000"]) == {"1", "2"}
    assert set(dataset_ids["euro_transaction"]) == {"4", "6", "9"}

if __name__ == "__main__":
    main()
