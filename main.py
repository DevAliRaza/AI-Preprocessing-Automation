import os
import shutil
import subprocess
import pandas as pd
from openai import OpenAI
import re

# Set your OpenAI API Key
OPENAI_API_KEY = "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"

def get_llm_generated_code(prompt):
    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI assistant that generates only executable Python code for preprocessing a DataFrame named 'df'. No comments, explanations, or markdowns."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def clean_generated_code(raw_code):
    cleaned_code = re.sub(r'```python', '', raw_code)
    cleaned_code = re.sub(r'```', '', cleaned_code)

    cleaned_code_lines = []
    for line in cleaned_code.split('\n'):
        stripped_line = line.strip()
        if not stripped_line.startswith("#") and stripped_line != "":
            cleaned_code_lines.append(line)

    return "\n".join(cleaned_code_lines).strip()

def save_data_and_code(df, code):
    os.makedirs('input', exist_ok=True)
    os.makedirs('output', exist_ok=True)

    df.to_csv('input/data.csv', index=False)

    with open('input/generated_code.py', 'w') as file:
        file.write(code)

def run_docker():
    subprocess.run(["docker", "build", "-t", "sandbox-runner", "."], check=True)

    subprocess.run([
        "docker", "run", "--rm",
        "-v", os.path.abspath("input") + ":/app/input",
        "-v", os.path.abspath("output") + ":/app/output",
        "sandbox-runner"
    ], check=True)

def collect_results():
    for filename in ["processed_data.csv", "report.pdf", "profile_report.html", "error.log", "missing_values_report.csv"]:
        src = os.path.join("output", filename)
        if os.path.exists(src):
            shutil.copy(src, filename)
            print(f"Collected: {filename}")

def main():
    df = pd.read_csv('input/data.csv')

    prompt = """
You are an automation assistant that generates Python code for data preprocessing and visualization.

Your task is to generate only executable Python code to process a DataFrame called `df`.

Preprocessing Requirements:
- Remove duplicate rows.
- Identify numeric columns and categorical columns.
- Convert numeric columns to numeric type and categorical columns to categorical type.
- Handle missing values by filling numeric columns with their median and categorical columns with their mode.
- Parse columns to datetime format if they contain "date" in the column name, but skip any that fail to parse.

Visualization Requirements:
- Create and save box plots for all numeric columns (each saved as 'boxplot_<column_name>.png').
- Create and save histograms for all numeric columns (each saved as 'histogram_<column_name>.png').
- Generate a numeric-only correlation heatmap (exclude non-numeric columns) and save it as 'report.pdf'.

Reports:
- Generate a Missing Values Report that includes:
    - Total missing values per column.
    - Percentage of missing values per column.
    - Save this report to 'missing_values_report.csv'.

- Generate a YData Profiling Report summarizing:
    - Column types, missing values, distributions, correlations, and key statistics.
    - Save this profiling report to 'profile_report.html'.

The final processed DataFrame must be saved to 'processed_data.csv'.

Return only the fully executable Python code with all necessary imports at the top.
Do not include any explanations, comments, or markdown formatting.
"""

    generated_code = get_llm_generated_code(prompt)
    cleaned_code = clean_generated_code(generated_code)

    save_data_and_code(df, cleaned_code)

    run_docker()

    collect_results()

if __name__ == '__main__':
    main()

