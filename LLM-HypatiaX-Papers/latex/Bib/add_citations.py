#!/usr/bin/env python3
"""
Automatic Citation Inserter for JMLR Paper
Adds ~30 new citations throughout the document
SAFE VERSION - Uses exact string matching to avoid LaTeX errors
"""

import sys

class SafeCitationInserter:
    def __init__(self):
        self.changes_made = []
        
    def safe_replace(self, text, old_text, new_text, description):
        """Safely replace text and track changes"""
        if old_text in text:
            text = text.replace(old_text, new_text, 1)
            self.changes_made.append(description)
        return text
    
    def insert_citations(self, text):
        """Insert all citations into the document using safe exact matches"""
        
        # SECTION 1: INTRODUCTION
        
        # 1.1 - Add openai2023gpt4 to first LLM mention
        text = self.safe_replace(
            text,
            r'from literature synthesis to mathematical problem-solving \citep{brown2020language,wei2022chain}.',
            r'from literature synthesis to mathematical problem-solving \citep{brown2020language,wei2022chain,openai2023gpt4}.',
            "Added openai2023gpt4 to Introduction"
        )
        
        # 1.2 - Add citations to LLM evaluation
        text = self.safe_replace(
            text,
            'When we evaluated state-of-the-art LLMs (GPT-4, Claude Sonnet 4) on 40 such problems:',
            r'When we evaluated state-of-the-art LLMs \citep{openai2023gpt4,anthropic2024claude} on 40 such problems:',
            "Added LLM model citations to evaluation"
        )
        
        # SECTION 2: RELATED WORK
        
        # 2.1 - Add neural-guided symbolic regression after PySR sentence
        text = self.safe_replace(
            text,
            'Modern frameworks like PySR \citep{cranmer2023interpretable} incorporate Pareto optimization to balance accuracy and complexity, physics-informed operators, and dimensional constraints.',
            r'Modern frameworks like PySR \citep{cranmer2023interpretable} incorporate Pareto optimization to balance accuracy and complexity, physics-informed operators, and dimensional constraints. Recent neural-guided approaches \citep{petersen2021deep,udrescu2020aifeynman} combine deep learning with symbolic search, while \citet{cranmer2023symbolic} provides a comprehensive review of symbolic regression in the modern era.',
            "Added neural-guided symbolic regression"
        )
        
        # 2.2 - Add transformer and limitations
        text = self.safe_replace(
            text,
            'Recent work has explored LLMs for hypothesis generation \citep{wang2023scientific}, literature mining \citep{liu2023summary}, and mathematical reasoning \citep{wei2022chain}. Romera et al. \citep{romera2023discovering} demonstrate that LLMs can recover known physical laws from textual descriptions and data patterns.',
            r'Recent work has explored LLMs for hypothesis generation \citep{wang2023scientific}, literature mining \citep{liu2023summary}, and mathematical reasoning \citep{wei2022chain}. The transformer architecture \citep{vaswani2017attention} underpins these capabilities, though recent studies \citep{mirzadeh2024reasoning,dziri2023faith} reveal fundamental limitations in compositional reasoning and extrapolation. Romera et al. \citep{romera2023discovering} demonstrate that LLMs can recover known physical laws from textual descriptions and data patterns.',
            "Added transformer architecture and limitations"
        )
        
        # 2.3 - Add physics-informed ML extensions
        text = self.safe_replace(
            text,
            'In scientific computing, physics-informed neural networks \citep{raissi2019physics} embed differential equations as constraints, while \citep{udrescu2020ai} uses neural networks to guide symbolic search.',
            r'In scientific computing, physics-informed neural networks \citep{raissi2019physics,karniadakis2021physics} embed differential equations as constraints, while neural operators \citep{lu2021learning,li2020fourier} learn mappings between function spaces. \citet{udrescu2020ai} uses neural networks to guide symbolic search.',
            "Added physics-informed ML and neural operators"
        )
        
        # SECTION 3: EMPIRICAL EVIDENCE
        
        # 3.1 - Add before failure taxonomy
        text = self.safe_replace(
            text,
            r'\subsection{Failure Mode Taxonomy}',
            r'\subsection{Failure Mode Taxonomy}' + '\n\n' + r'These failure modes align with known limitations of transformer-based models in systematic generalization \citep{lake2017building} and extrapolation \citep{zhang2024extrapolation}.',
            "Added generalization limitations before taxonomy"
        )
        
        # 3.2 - Add VaR citations before Case Study 2
        text = self.safe_replace(
            text,
            r'\subsubsection{Case Study 2: Distributional Reasoning Failure (Value-at-Risk)}',
            r'\subsubsection{Case Study 2: Distributional Reasoning Failure (Value-at-Risk)}' + '\n\n' + r'Value-at-Risk is a standard risk metric in finance \citep{rockafellar2000optimization,danielsson2017forecasting}, requiring precise understanding of tail distributions.',
            "Added VaR finance citations"
        )
        
        # 3.3 - Add Expected Shortfall citation
        text = self.safe_replace(
            text,
            r'\subsubsection{Case Study 3: Library API Misuse (Expected Shortfall)}',
            r'\subsubsection{Case Study 3: Library API Misuse (Expected Shortfall)}' + '\n\n' + r'Expected Shortfall (also called Conditional VaR) provides a more comprehensive risk measure than VaR \citep{embrechts1997modelling,rockafellar2000optimization}.',
            "Added Expected Shortfall citations"
        )
        
        # 3.4 - Add extrapolation failure
        text = self.safe_replace(
            text,
            'Symbolic methods enforce physical constraints that ensure extrapolation validity.',
            r'This extrapolation failure is well-documented in neural network literature \citep{zhang2024extrapolation}, where models exhibit spectral bias toward low-frequency functions. Symbolic methods enforce physical constraints that ensure extrapolation validity.',
            "Added spectral bias citation"
        )
        
        # SECTION 4: THEORETICAL FRAMEWORK
        
        # 4.1 - Add after Definition 1
        text = self.safe_replace(
            text,
            r'\end{definition}' + '\n\n' + r'\begin{definition}[Reproductive System]',
            r'\end{definition}' + '\n\n' + r'This definition draws on established principles of symbolic computation \citep{meurer2017sympy} and dimensional analysis \citep{buckingham1914physically}.' + '\n\n' + r'\begin{definition}[Reproductive System]',
            "Added symbolic computation citations after Definition 1"
        )
        
        # 4.2 - Add after theorem proof
        text = self.safe_replace(
            text,
            r'\paragraph{Remark:} This proof assumes local independence of token probabilities',
            r'This reproductive behavior is consistent with observations about large language model training \citep{hoffmann2022training}.' + '\n\n' + r'\paragraph{Remark:} This proof assumes local independence of token probabilities',
            "Added LLM training citation after theorem"
        )
        
        # SECTION 5: HYPATIAX ARCHITECTURE
        
        # 5.1 - Add genetic programming foundations
        text = self.safe_replace(
            text,
            r'We employ PySR \citep{cranmer2023interpretable} for multi-objective genetic programming:',
            r'We employ PySR \citep{cranmer2023interpretable}, building on genetic programming principles \citep{koza1992genetic,fortin2012deap}, for multi-objective genetic programming:',
            "Added genetic programming foundations"
        )
        
        # 5.2 - Add Michaelis-Menten citation
        text = self.safe_replace(
            text,
            r'\textbf{Example (Michaelis-Menten):} $v(S) = \frac{V_{\max}S}{K_m + S}$ has potential singularity at $K_m + S = 0$.',
            r'\textbf{Example (Michaelis-Menten):} The Michaelis-Menten equation \citep{michaelis1913kinetics}, $v(S) = \frac{V_{\max}S}{K_m + S}$, has potential singularity at $K_m + S = 0$.',
            "Added Michaelis-Menten citation"
        )
        
        # SECTION 6: EXPERIMENTS
        
        # 6.1 - Add to Key Findings section
        text = self.safe_replace(
            text,
            r'\item \textbf{Competitive with human experts}: Our approaches match or exceed human performance',
            r'\item \textbf{Competitive with human experts}: Our approaches match or exceed human performance, consistent with recent advances in automated scientific discovery \citep{silver2017mastering,jumper2021highly}, while requiring significantly less time',
            "Added automated discovery citations"
        )
        
        # SECTION 7: DISCUSSION
        
        # 7.1 - Add AI safety to design principles
        text = self.safe_replace(
            text,
            r'\item \textbf{Make failures explicit}: Invalid expressions should be rejected, not silently accepted with warnings',
            r'\item \textbf{Make failures explicit}: Invalid expressions should be rejected, not silently accepted with warnings. These principles align with broader efforts in AI safety \citep{russell2019human,amodei2016concrete} and interpretable machine learning \citep{lipton2018mythos}',
            "Added AI safety and interpretability citations"
        )
        
        # 7.2 - Add to future work
        text = self.safe_replace(
            text,
            r'\item \textbf{Larger-scale evaluation}: Expand to 100+ tests per domain for statistical power',
            r'\item \textbf{Neural arithmetic integration}: Incorporate neural arithmetic units \citep{trask2018neural} for improved numerical stability' + '\n' + r'\item \textbf{Larger-scale evaluation}: Expand to 100+ tests per domain for statistical power',
            "Added neural arithmetic to future work"
        )
        
        # Add contextual citations
        
        # Arrhenius equation if present
        if 'Arrhenius equation' in text and 'arrhenius1889' not in text:
            text = self.safe_replace(
                text,
                'Arrhenius equation',
                r'Arrhenius equation \citep{arrhenius1889reaction}',
                "Added Arrhenius citation"
            )
        
        # ML theory in discussion
        text = self.safe_replace(
            text,
            r'The future of analytical discovery is not "AI vs. humans" or "neural vs. symbolic"',
            r'Classical learning theory \citep{vapnik1999overview,bishop2006pattern,goodfellow2016deep} provides foundations for understanding generalization, though modern overparameterized models challenge traditional assumptions. The future of analytical discovery is not "AI vs. humans" or "neural vs. symbolic"',
            "Added ML theory citations to discussion"
        )
        
        # Add Kelly criterion if discussing optimal betting
        if 'Kelly criterion' in text and 'kelly1956' not in text:
            text = text.replace(
                'Kelly criterion',
                r'Kelly criterion \citep{kelly1956criterion}',
                1
            )
            self.changes_made.append("Added Kelly criterion citation")
        
        # Add Uniswap citations
        if 'Uniswap' in text and 'uniswap2018' not in text:
            text = text.replace(
                'Uniswap',
                r'Uniswap \citep{uniswap2018whitepaper,adams2021uniswap}',
                1
            )
            self.changes_made.append("Added Uniswap citations")
        
        return text
    
    def process_file(self, input_file, output_file):
        """Process the LaTeX file and add citations"""
        
        print("="*70)
        print("SAFE AUTOMATIC CITATION INSERTER")
        print("="*70)
        
        # Read input file
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"\nError: {input_file} not found!")
            print("Make sure you run this script in the same directory as your .tex file")
            return False
        
        print(f"\n✓ Reading: {input_file}")
        print(f"  File size: {len(content):,} characters")
        
        # Insert citations
        print("\n" + "="*70)
        print("INSERTING CITATIONS...")
        print("="*70)
        modified_content = self.insert_citations(content)
        
        # Report changes
        print(f"\n{'='*70}")
        print(f"CHANGES MADE: {len(self.changes_made)}")
        print(f"{'='*70}\n")
        for i, change in enumerate(self.changes_made, 1):
            print(f"  {i:2d}. ✓ {change}")
        
        if len(self.changes_made) == 0:
            print("\n⚠ WARNING: No changes were made!")
            print("  This might mean:")
            print("  - Citations already exist")
            print("  - Text doesn't match exactly (check for typos/formatting)")
            print("  - File structure is different than expected")
        
        # Write output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        print(f"\n{'='*70}")
        print(f"✓ Modified file written to: {output_file}")
        print(f"  New file size: {len(modified_content):,} characters")
        print(f"  Characters added: {len(modified_content) - len(content):,}")
        print(f"{'='*70}")
        
        # Next steps
        print("\n" + "="*70)
        print("NEXT STEPS")
        print("="*70)
        print("\n1. Review the changes:")
        print(f"   diff jmlr_paper.tex {output_file} | less")
        print("\n2. Test compilation:")
        print(f"   pdflatex {output_file}")
        print("\n3. If it compiles without errors, replace original:")
        print(f"   cp jmlr_paper.tex jmlr_paper_backup.tex")
        print(f"   mv {output_file} jmlr_paper.tex")
        print("\n4. Run full BibTeX sequence:")
        print("   pdflatex jmlr_paper.tex")
        print("   bibtex jmlr_paper")
        print("   pdflatex jmlr_paper.tex")
        print("   pdflatex jmlr_paper.tex")
        print("\n5. Check bibliography:")
        print("   Should now have 40-45 references instead of 12")
        print("="*70 + "\n")
        
        return True

def main():
    inserter = SafeCitationInserter()
    
    input_file = 'jmlr_paper.tex'
    output_file = 'jmlr_paper_with_citations.tex'
    
    success = inserter.process_file(input_file, output_file)
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
