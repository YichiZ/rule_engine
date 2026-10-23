from collections import defaultdict

_dataset = [
    {"id": "1", "currency": "USD"},
    {"id": "2", "amount": 10001, "currency": "USD"},
    {"id": "3", "amount": 10000, "currency": "CAD"},
    {"id": "4", "amount": 15000, "currency": "EUR"},
    {"id": "5", "amount": 100, "currency": "YUAN"},
    {"id": "6", "amount": 99, "currency": "EUR"},
    {"id": "7", "amount": 50, "currency": "CAD"},
    {"id": "8", "amount": 0, "currency": "USD"},
    {"id": "9", "amount": 20000, "currency": "YUAN"},
    {"id": "10", "amount": "15000", "currency": "USD"},
    {"id": "11", "amount": 15000, "currency": "eur"},
    {"id": "12", "amount": 16000, "currency": "EUR "},
    {"id": "13", "amount": None, "currency": "CAD"},
    {"id": "14", "amount": -1, "currency": "USD"},
    {"id": "15", "currency": None},
    {"id": "16", "amount": 14000},
    {"id": "17", "amount": 99.5, "currency": "YUAN"},
    {"id": "18", "amount": 0.0, "currency": "usd"},
    {"id": "19", "amount": "USD", "currency": 20000},
    {"id": "20", "amount": 10001, "currency": "USD", "note": "dup", "flagged": True},
    {"id": "21"},
    {"id": "22", "amount": 15999, "currency": ""},
    {"id": "23", "amount": 1, "currency": "Yuan"},
    {"id": "24", "amount": 100000, "currency": "CAD", "account": "123"},
]

_rulesets = [
    {
        "id": "1",
        "name": "High_Value_Band",
        "combinator": "AND",
        "conditions": [
            {"field": "amount", "operator": ">", "value": 14000},
            {"field": "amount", "operator": "<", "value": 16000},
        ],
        "action": "SendAlert",
    },
    {
        "id": "2",
        "name": "Small_Positive",
        "combinator": "AND",
        "conditions": [
            {"field": "amount", "operator": ">", "value": 0},
            {"field": "amount", "operator": "<", "value": 100},
        ],
        "action": "FlagReview",
    },
    {
        "id": "3",
        "name": "Zero_or_Above_16000",
        "combinator": "OR",
        "conditions": [
            {"field": "amount", "operator": "==", "value": 0},
            {"field": "amount", "operator": ">", "value": 16000},
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
            {"field": "amount", "operator": ">", "value": 10000},
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
]

from collections import defaultdict

class RuleEngine:
    def add_conditions(self, conditions) -> list:
        fncs = []
        for condition in conditions:
            if condition["operator"] == ">":
                fcn = lambda x, field=condition["field"], value=condition["value"]: (
                    x[field] > value
                )
                fncs.append(fcn)
            elif condition["operator"] == "<":
                fcn = lambda x, field=condition["field"], value=condition["value"]: (
                    x[field] < value
                )
                fncs.append(fcn)
            elif condition["operator"] == "==":
                fcn = lambda x, field=condition["field"], value=condition["value"]: (
                    x[field] == value
                )
                fncs.append(fcn)
        return fncs

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
                fcns = [rule(data) for rule in rules]
                if all(fcns):
                    result.append(data)
            res[rule_name] = result

        return res


def main() -> None:
    rule_engine = RuleEngine(_rulesets)
    res = rule_engine.execute(_dataset)

    dataset_ids = {}
    
    for rulename, transactions in res.items():
        dataset_ids[rulename] = [transaction["id"] for transaction in transactions]
    
    assert set(dataset_ids["High_Value_Band"]) == {"4"}
    assert set(dataset_ids["Small_Positive"]) == {"6", "7"}
    assert set(dataset_ids["Zero_or_Above_16000"]) == {"8", "9"}
    assert set(dataset_ids["USD_or_EUR"]) == {"1", "2", "4", "6", "8"}
    assert set(dataset_ids["Large_USD"]) == {"2"}
    assert set(dataset_ids["Euro"]) == {"4", "6"}

if __name__ == "__main__":
    main()
