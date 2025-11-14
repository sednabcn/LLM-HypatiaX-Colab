#🎨 Creating Custom Demos
#Simple CLI Demo

from demo.engine import HypatiaXEngine
from demo.ui import UIComponents

def run_simple_demo():
    engine = HypatiaXEngine()
    ui = UIComponents()
    
    print(ui.header("Simple HypatiaX Demo"))
    
    while True:
        query = input("\nEnter query (or 'quit'): ").strip()
        if query.lower() == 'quit':
            break
        
        result = engine.process(query)
        print(ui.formula_display(result.formula, result.confidence))

if __name__ == '__main__':
    run_simple_demo()
