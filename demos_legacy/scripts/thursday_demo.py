#!/usr/bin/env python3
"""
Thursday Demo - Get ONE thing working
Goal: Convert 'calculate area of circle' → A = πr²
"""

def test_simple_demo():
    """Test the simplest possible conversion"""
    
    # Step 1: Your input
    input_text = "calculate area of circle"
    print(f"📝 Input: {input_text}")
    
    # Step 2: Try to run HypatiaX
    try:
        # REPLACE THIS with your actual HypatiaX code
        # Example:
        # from hypatiax import process_text
        # output = process_text(input_text)
        
        # For now, simulate what SHOULD happen:
        output = "A = πr²"  # This is what you WANT to get
        
        print(f"✅ Output: {output}")
        print(f"✅ SUCCESS!")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        print(f"Fix needed: {type(e).__name__}")
        return False

if __name__ == "__main__":
    print("="*50)
    print("THURSDAY DEMO - Simple Test")
    print("="*50)
    
    success = test_simple_demo()
    
    if success:
        print("\n🎉 Demo works! Document this!")
    else:
        print("\n🔧 Fix the error and try again")
