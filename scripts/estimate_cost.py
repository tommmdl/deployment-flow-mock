import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--rates", required=True)
args = parser.parse_args()
rates = json.loads(Path(args.rates).read_text())
keys = ["eks_hour", "ec2_hour", "nat_hour", "ipv4_hour", "gp3_gib_month"]
if not all(isinstance(rates.get(k), (int, float)) and rates[k] > 0 for k in keys):
    raise SystemExit("Preencha tarifas oficiais positivas; placeholders não são estimativas")
if not all(rates.get(k) for k in ["region", "date", "source"]):
    raise SystemExit("Informe região, data e fonte das tarifas")
items = {
    "EKS": 730 * rates["eks_hour"],
    "EC2": 2 * 730 * rates["ec2_hour"],
    "NAT": 2 * 730 * rates["nat_hour"],
    "IPv4": 2 * 730 * rates["ipv4_hour"],
    "EBS gp3": 40 * rates["gp3_gib_month"],
}
for name, cost in items.items():
    print(f"{name}: USD {cost:.2f}/mês")
print(f"Subtotal fixo: USD {sum(items.values()):.2f}/mês; acrescentar tráfego, logs, S3 e impostos")
