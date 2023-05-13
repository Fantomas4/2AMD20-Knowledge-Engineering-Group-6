import pandas as pd
import sweetviz as sv

# Load the dataset (example: iris dataset)
df = pd.read_csv('datasets/CBP2020.CB2000CBP-2023-05-13T223306.csv')

# Generate the analysis report
report = sv.analyze(df)

# Display the report in the browser
report.show_html('cbp_report.html')