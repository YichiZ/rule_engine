_dataset = [
  { "amount": 15000, "currency": "USD" },
  { "amount": 10001, "currency": "USD" },
  { "amount": 10000, "currency": "USD" },
  { "amount": 15000, "currency": "EUR" },
  { "amount": 100, "currency": "USD" },
  { "amount": 99, "currency": "EUR" },
  { "amount": 50, "currency": "USD" },
  { "amount": 0, "currency": "USD" },
  { "amount": 20000 }
]

_ruleset = [
  {
    "id": "1",
    "name": "High Value Transaction",
    "conditions": [
      { "field": "amount", "operator": ">", "value": 14000 },
      { "field": "amount", "operator": "<", "value": 16000 }
    ],
    "action": "SendAlert"
  },
]

class RuleEngine:
    def __init__(self, rules):
        self.rules = []

        for rule in rules:
            if rule["operator"] == ">":
                fcn = lambda x, field=rule["field"], value=rule["value"]: x[field] > value
                self.rules.append(fcn)
            elif rule["operator"] == "<":
                fcn = lambda x, field=rule["field"], value=rule["value"]: x[field] < value
                self.rules.append(fcn)
            elif rule["operator"] == "==":
                fcn = lambda x, field=rule["field"], value=rule["value"]: x[field] == value
                self.rules.append(fcn)

    def execute(self, dataset):
        result = []
        for data in dataset:
            fcns = [rule(data) for rule in self.rules]
            if all(fcns):
                result.append(data)
        print(result)

def main() -> None:
    rule_engine = RuleEngine(_ruleset[0]["conditions"])
    rule_engine.execute(_dataset)

if __name__ == "__main__":
    main()
