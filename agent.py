import os
import argparse
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import pandas as pd
import importlib.util

#load environment variables
load_dotenv()

#initialize llm
def get_llm():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise ValueError("Set GROQ_API_KEY in .env")
    return ChatGroq(api_key=key, model="llama-3.1-8b-instant", temperature=0.3)

#state class
class State:
    def __init__(self, target_bank, pdf_path, csv_path):
        self.target_bank = target_bank
        self.pdf_path = pdf_path
        self.csv_path = csv_path
        self.parser_code = ""
        self.test_result = ""
        self.error_message = ""
        self.attempt = 1

#analyze files
def analyze(state):
    print(f"Analyzing files for {state.target_bank}")
    print("PDF:", state.pdf_path)
    print("CSV:", state.csv_path)
    return state

#use llm to generate the parser code
def generate(state):
    print(f"Generating parser code, attempt {state.attempt}...")
    
    llm = get_llm()
    
    #if this is a retry,add the error message to help the llm fix it
    error_info = ""
    if state.attempt > 1:
        error_info = f"\n\nPREVIOUS ERROR: {state.error_message}\nPlease fix this error."
    
    prompt = f"""
        Generate a Python parser for {state.target_bank} bank statements.

        Requirements:
        1. Define a function: parse(pdf_path: str) -> pd.DataFrame
        2. Use tabula-py to extract tables from PDF
        3. Return DataFrame with EXACT columns: Date, Description, Debit Amt, Credit Amt, Balance
        4. Keep column names exactly as they are - do NOT rename them
        5. Convert Debit Amt, Credit Amt, and Balance to float (handle empty values as NaN)
        6. Only import: pandas, tabula
        7. IMPORTANT: Return ONLY the Python code. Do NOT wrap it in ```python or ``` markdown blocks.
        8. Do NOT include any explanations, comments, or text outside the code.

{error_info}
"""
    
    response = llm.invoke(prompt)
    code = response.content.strip()
    
    #just in case llm ignores instructions
    if code.startswith("```python"):
        code = code[9:].strip()
    if code.startswith("```"):
        code = code[3:].strip()
    if code.endswith("```"):
        code = code[:-3].strip()
    
    state.parser_code = code
    return state

#testing if the parser works
def test(state):
    print("Testing parser...")
    
    #make sure directory exists
    os.makedirs("custom_parsers", exist_ok=True)
    parser_file = f"custom_parsers/{state.target_bank}_parser.py"
    
    try:
        #save the generated code to a file
        with open(parser_file, "w") as f:
            f.write(state.parser_code)
        
        #import the parser file 
        spec = importlib.util.spec_from_file_location("parser_module", parser_file)
        parser_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(parser_module)
        
        #run the parse function
        result_df = parser_module.parse(state.pdf_path)
        
        #load the expected results
        expected_df = pd.read_csv(state.csv_path)
        
        #checking if they match
        if result_df.equals(expected_df):
            state.test_result = "success"
            print("Test passed!")
        else:
            # Maybe the types are different? Try this
            pd.testing.assert_frame_equal(result_df, expected_df, check_dtype=False)
            state.test_result = "success"
            print("Test passed!")
            
    except Exception as e:
        #test failed
        state.test_result = "failed"
        state.error_message = str(e)
        state.attempt += 1
        print(f"Test failed: {e}")
    
    return state

#main function
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    args = parser.parse_args()
    
    #setup the state
    state = State(
        target_bank=args.target,
        pdf_path=f"data/{args.target}/{args.target}_sample.pdf",
        csv_path=f"data/{args.target}/results.csv"
    )
    
    #analyze
    state = analyze(state)
    
    #generate and test up to 3 times
    while state.attempt <= 3 and state.test_result != "success":
        state = generate(state)
        state = test(state)
    
    # Done
    print("\n" + "="*50)
    print("Result:", state.test_result)
    if state.test_result == "success":
        print(f"Parser saved to: custom_parsers/{args.target}_parser.py")
        
    else:
        print("Failed after 3 attempts")
        print("Last error:", state.error_message)
    print("="*50)

if __name__ == "__main__":
    main()