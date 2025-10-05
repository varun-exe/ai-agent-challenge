# AI Agent Challenge - PDF Bank Statement Parser

An autonomous agent that generates custom Python parsers for bank statement PDFs using LLM-powered code generation and self-correction.

## How It Works

The agent follows a simple loop: it analyzes the input PDF and expected CSV, uses an LLM (Groq's Llama) to generate a parser function, tests the output against the expected results, and if the test fails, feeds the error back to the LLM to self-correct (up to 3 attempts). The agent stops when it either generates a working parser or exhausts all retry attempts.

## Setup Instructions

### Step 1: Clone the Repository
```bash
git clone <your-repo-url>
cd ai-agent-challenge
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv karbon-env
source karbon-env/bin/activate  # On Windows: karbon-env\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables
```bash
GROQ_API_KEY=your_groq_api_key_here
```
Get your API key from Groq Console


### Step 5: Run the Agent
```bash
python agent.py --target icici
```

## Output
The agent generates a parser file at `custom_parsers/{bank_name}_parser.py` with a `parse(pdf_path: str) -> pd.DataFrame` function that extracts transactions with columns: Date, Description, Debit Amt, Credit Amt, Balance.


## Notes
- The agent attempts up to 3 times to generate a working parser
- Each retry includes the previous error message to help the LLM self-correct
- The generated parser uses tabula-py for PDF table extraction

