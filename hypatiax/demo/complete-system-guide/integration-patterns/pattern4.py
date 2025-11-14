# Pattern 4: Full Interactive Demo

from demo.engine import HypatiaXEngine
from demo.ui import InteractiveDemo
from demo.examples import ExampleManager

# Initialize components
engine = HypatiaXEngine()
manager = ExampleManager()

# Run interactive demo
demo = InteractiveDemo(engine)
demo.run()  # Full menu-driven interface
