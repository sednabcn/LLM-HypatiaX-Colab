import json
from pathlib import Path

# Merge all LLM baseline files
llm_files = sorted(Path(".").glob("baseline_*llm*.json"))
all_llm = []
for f in llm_files:
    print(f"Reading {f}...")
    data = json.load(open(f))
    if isinstance(data, list):
        all_llm.extend(data)

# Merge all NN baseline files
nn_files = sorted(Path(".").glob("baseline_nn*.json"))
all_nn = []
for f in nn_files:
    print(f"Reading {f}...")
    data = json.load(open(f))
    if isinstance(data, list):
        all_nn.extend(data)

# Save merged files
with open("baseline_llm_ALL_MERGED.json", "w") as f:
    json.dump(all_llm, f, indent=2)

with open("baseline_nn_ALL_MERGED.json", "w") as f:
    json.dump(all_nn, f, indent=2)

# Get unique domains
llm_domains = set(t["domain"] for t in all_llm if "domain" in t)
nn_domains = set(t["domain"] for t in all_nn if "domain" in t)

print(f"\n✅ Merged LLM: {len(all_llm)} test cases across {len(llm_domains)} domains")
print(f"   Domains: {', '.join(sorted(llm_domains))}")
print(f"\n✅ Merged NN: {len(all_nn)} test cases across {len(nn_domains)} domains")
print(f"   Domains: {', '.join(sorted(nn_domains))}")
print(f"\n📁 Saved to:")
print(f"   - baseline_llm_ALL_MERGED.json")
print(f"   - baseline_nn_ALL_MERGED.json")
