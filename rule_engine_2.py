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
    {
        "id": "7",
        "name": "No_Country",
        "combinator": "AND",
        "conditions": [
            {"field": "country", "operator": "==", "value": "US"},
        ],
        "action": "Reject",
    },
    {
        "id": "8",
        "name": "No_Status",
        "combinator": "AND",
        "conditions": [
            {"field": "status", "operator": "==", "value": "open"},
        ],
        "action": "Reject",
    },
    {
        "id": "9",
        "name": "No_Customer",
        "combinator": "AND",
        "conditions": [
            {"field": "customer", "operator": "==", "value": "c1"},
        ],
        "action": "Reject",
    },
    {
        "id": "10",
        "name": "Wrong_Account",
        "combinator": "AND",
        "conditions": [
            {"field": "account", "operator": "==", "value": "999"},
        ],
        "action": "Hold",
    },
    {
        "id": "11",
        "name": "Wrong_Note",
        "combinator": "AND",
        "conditions": [
            {"field": "note", "operator": "==", "value": "missing"},
        ],
        "action": "FlagReview",
    },
    {
        "id": "12",
        "name": "Not_Flagged",
        "combinator": "AND",
        "conditions": [
            {"field": "flagged", "operator": "==", "value": False},
        ],
        "action": "Log",
    },
    {
        "id": "13",
        "name": "Missing_Channel",
        "combinator": "AND",
        "conditions": [
            {"field": "channel", "operator": "==", "value": "web"},
            {"field": "amount", "operator": ">", "value": 0},
        ],
        "action": "SendAlert",
    },
    {
        "id": "14",
        "name": "Region_EU",
        "combinator": "OR",
        "conditions": [
            {"field": "region", "operator": "==", "value": "EU"},
            {"field": "currency", "operator": "==", "value": "EUR"},
        ],
        "action": "HoldEUR",
    },
    {
        "id": "15",
        "name": "Negative_Large",
        "combinator": "AND",
        "conditions": [
            {"field": "amount", "operator": "<", "value": 0},
            {"field": "amount", "operator": ">", "value": 10000},
        ],
        "action": "Escalate",
    },
    {
        "id": "16",
        "name": "Exact_Yuan_Zero",
        "combinator": "AND",
        "conditions": [
            {"field": "amount", "operator": "==", "value": 0},
            {"field": "currency", "operator": "==", "value": "YUAN"},
        ],
        "action": "Reject",
    },
]

class RuleEngine:
    # This should be just 
    def add_conditions(self, conditions, combinator) -> list:
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

        if combinator == "AND":
            return lambda x: all(fnc(x) for fnc in fncs)
        if combinator == "OR":
            return lambda x: any(fnc(x) for fnc in fncs)

    def __init__(self, rulesets):
        self.rulesFncs = defaultdict(list)

        for ruleset in rulesets:
            self.rulesFncs[ruleset["name"]] = {"conditions": self.add_conditions(ruleset["conditions"], ruleset["combinator"])}

    def execute(self, dataset):
        self.res = defaultdict(list)
        self.failures = defaultdict(list)
        for rule_name, rules in self.rulesFncs.items():
            fcn = rules["conditions"]
            for data in dataset:
                try:
                    if fcn(data):
                        self.res[rule_name].append(data)
                except:
                    self.failures[rule_name].append(data)

        return self.res


def main() -> None:
    rule_engine = RuleEngine(_rulesets)
    res = rule_engine.execute(_dataset)

    dataset_ids = {}
    
    for rulename, transactions in res.items():
        dataset_ids[rulename] = [transaction["id"] for transaction in transactions]
    
    failure_ids = {
        rulename: [transaction["id"] for transaction in transactions]
        for rulename, transactions in rule_engine.failures.items()
    }
    every_id = {str(i) for i in range(1, 25)}

    print(res)

    assert set(dataset_ids.get("High_Value_Band", [])) == {"4", "11", "22"}
    assert set(dataset_ids.get("Small_Positive", [])) == {"6", "7", "17", "23"}
    assert set(dataset_ids.get("Zero_or_Above_16000", [])) == {"8", "9", "18", "24"}
    assert set(dataset_ids.get("USD_or_EUR", [])) == {
        "1",
        "2",
        "4",
        "6",
        "8",
        "10",
        "14",
        "20",
    }
    assert set(dataset_ids.get("Large_USD", [])) == {"2", "20"}
    assert set(dataset_ids.get("Euro", [])) == {"4", "6"}
    assert set(dataset_ids.get("No_Country", [])) == set()
    assert set(dataset_ids.get("No_Status", [])) == set()
    assert set(dataset_ids.get("No_Customer", [])) == set()
    assert set(dataset_ids.get("Wrong_Account", [])) == set()
    assert set(dataset_ids.get("Wrong_Note", [])) == set()
    assert set(dataset_ids.get("Not_Flagged", [])) == set()
    assert set(dataset_ids.get("Missing_Channel", [])) == set()
    assert set(dataset_ids.get("Region_EU", [])) == set()
    assert set(dataset_ids.get("Negative_Large", [])) == set()
    assert set(dataset_ids.get("Exact_Yuan_Zero", [])) == set()

    assert set(failure_ids.get("High_Value_Band", [])) == {"1", "10", "13", "15", "19", "21"}
    assert set(failure_ids.get("Small_Positive", [])) == {"1", "10", "13", "15", "19", "21"}
    assert set(failure_ids.get("Zero_or_Above_16000", [])) == {"1", "10", "13", "15", "19", "21"}
    assert set(failure_ids.get("USD_or_EUR", [])) == {"16", "21"}
    assert set(failure_ids.get("Large_USD", [])) == {"1", "10", "16", "21"}
    assert set(failure_ids.get("Euro", [])) == {"16", "21"}
    assert set(failure_ids.get("No_Country", [])) == every_id
    assert set(failure_ids.get("No_Status", [])) == every_id
    assert set(failure_ids.get("No_Customer", [])) == every_id
    assert set(failure_ids.get("Wrong_Account", [])) == every_id - {"24"}
    assert set(failure_ids.get("Wrong_Note", [])) == every_id - {"20"}
    assert set(failure_ids.get("Not_Flagged", [])) == every_id - {"20"}
    assert set(failure_ids.get("Missing_Channel", [])) == every_id
    assert set(failure_ids.get("Region_EU", [])) == every_id
    assert set(failure_ids.get("Negative_Large", [])) == {"1", "10", "13", "15", "19", "21"}
    assert set(failure_ids.get("Exact_Yuan_Zero", [])) == {"1", "15", "21"}

if __name__ == "__main__":
    main()
