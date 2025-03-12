
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from ydata_profiling import ProfileReport
from fpdf import FPDF
import traceback
import os
import shutil

try:
    df = pd.read_csv('/app/input/data.csv')

    with open('/app/input/generated_code.py', 'r') as file:
        user_code = file.read()

    # Safe environment to execute user-generated code
    safe_globals = {
        "__builtins__": {
            "print": print,
            "len": len,
            "range": range,
            "sum": sum,
            "min": min,
            "max": max,
            "sorted": sorted,
            "dict": dict,
            "list": list,
            "set": set,
            "tuple": tuple,
            "str": str,
            "object": object,
            "__import__": __import__,
        },
        "pd": pd,
        "np": np,
        "plt": plt,
        "sns": sns,
        "MinMaxScaler": MinMaxScaler,
        "LabelEncoder": LabelEncoder,
        "ProfileReport": ProfileReport,
        "FPDF": FPDF,
        "df": df,
        "ValueError": ValueError
    }

    # Execute the LLM-generated preprocessing code
    exec(user_code, safe_globals)

    # Get the processed DataFrame back from the safe globals
    processed_df = safe_globals.get("df", df)

    # Save processed data
    processed_df.to_csv('/app/output/processed_data.csv', index=False)

    # Move profiling report if generated
    if os.path.exists("profile_report.html"):
        shutil.move("profile_report.html", "/app/output/profile_report.html")

    # Generate correlation heatmap (only for numeric columns)
    numeric_cols = processed_df.select_dtypes(include=[np.number]).columns

    if len(numeric_cols) > 0:
        plt.figure(figsize=(10, 8))
        sns.heatmap(processed_df[numeric_cols].corr(), annot=True, cmap='coolwarm')
        plt.savefig('/app/output/report.pdf')
    else:
        with open('/app/output/error.log', 'a') as error_file:
            error_file.write("No numeric columns available for correlation heatmap.\n")

except Exception as e:
    with open('/app/output/error.log', 'w') as error_file:
        error_file.write(traceback.format_exc())

