import json
from pathlib import Path
from datetime import datetime, timedelta

class ContractGenerator:
    def __init__(self):
        self.tmpl_dir = Path.home() / ".picoclaw" / "skills" / "templates"
        self.out_dir = Path.home() / ".picoclaw" / "workspace" / "contracts"
        self.out_dir.mkdir(parents=True, exist_ok=True)
    
    def render(self, template_name, context):
        path = self.tmpl_dir / f"{template_name}.md"
        if not path.exists():
            return f"# Template {template_name} not found"
        text = path.read_text()
        for key, val in context.items():
            text = text.replace(f"{{{{{key}}}}}", str(val))
        return text
    
    def generate(self, deal):
        ctx = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "client_name": "CLIENT_NAME_TBD",
            "project_title": deal.get("lead_title", "Untitled"),
            "deliverable": "Deliverables per job description",
            "client_price": deal.get("revenue", 0),
            "provider_price": deal.get("cost", 0),
            "provider_name": deal.get("provider_name", "Provider"),
            "payment_method": "Wise",
            "start_date": datetime.now().strftime("%Y-%m-%d"),
            "delivery_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        }
        client_md = self.render("client_contract", ctx)
        sub_md = self.render("subcontract", ctx)
        
        base = self.out_dir / f"{deal['lead_id']}_{deal['provider_id']}"
        base.mkdir(parents=True, exist_ok=True)
        (base / "client_contract.md").write_text(client_md)
        (base / "subcontract.md").write_text(sub_md)
        return str(base)

if __name__ == "__main__":
    cg = ContractGenerator()
    mock = {"lead_id": "m1", "provider_id": "p2", "lead_title": "Python API Dev", "revenue": 500, "cost": 200, "provider_name": "Boutique Studio B"}
    path = cg.generate(mock)
    print(f"Contracts written to: {path}")

