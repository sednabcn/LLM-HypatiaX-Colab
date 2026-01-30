──(py312)(agagora㉿localhost)-[~/Downloads/GITHUB/LLM-HypatiaX-Colab]
└─$ python results/parse_txt_to_json.py
================================================================================
PARSING TEXT FILES TO JSON FORMAT
================================================================================

🔵 Parsing LLM files...
  📄 baseline_neural_pure_llm_20251220_1951.txt
     ✅ Extracted 0 test cases
     Domains: []
  📄 baseline_pure_llm_202512_152604.txt
     ✅ Extracted 20 test cases
     Domains: ['chemistry', 'fluids', 'materials', 'mechanics', 'thermodynamics']

🔴 Parsing NN files...
  📄 baseline_neural_network_2251221_1033.txt
     ✅ Extracted 0 test cases
     Domains: []
  📄 baseline_neural_network_all.txt
     ✅ Extracted 20 test cases
     Domains: ['chemistry', 'fluids', 'materials', 'mechanics', 'thermodynamics']

✅ Saved LLM: results/baseline_llm_PARSED.json (20 cases)
✅ Saved NN: results/baseline_nn_PARSED.json (20 cases)

================================================================================
SUMMARY
================================================================================

📊 Total parsed:
   LLM: 20 test cases across 5 domains
   NN:  20 test cases across 5 domains

✅ Common domains: ['chemistry', 'fluids', 'materials', 'mechanics', 'thermodynamics']

================================================================================
READY FOR COMPARISON
================================================================================

Run comparison with:
  python results/comparison_analysis_improved.py results/baseline_llm_PARSED.json results/baseline_nn_PARSED.json

┌──(py312)(agagora㉿localhost)-[~/Downloads/GITHUB/LLM-HypatiaX-Colab]
└─$
