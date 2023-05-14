import pandas as pd
import sweetviz as sv

# Load the dataset (example: iris dataset)
df_1 = pd.read_csv('datasets/CBP2019.CB1900CBP-2023-05-14T012245.csv')
df_2 = pd.read_csv('datasets/Bachelor_Degree_Majors.csv')

# Get the common values between the two columns
common_values = pd.Series(list(set(df_1['Geographic Area Name (NAME)']).intersection(set(df_2['State']))))
print("\n> States included both in CBP and in Bachelor Majors dataset: {}".format(len(common_values)))
print(common_values)

# Get the non-common values between the two columns
symmetric_difference = pd.Series(list(set(df_1['Geographic Area Name (NAME)']).symmetric_difference(set(df_2['State']))))
print("\n> States included in CBP but not in Bachelor Majors dataset: {}".format(len(symmetric_difference)))
print(symmetric_difference)

# We will to drop the rows in df_1 that contain any of the non-common (State) values.
# Drop rows containing the specified values
df_1 = df_1[~df_1['Geographic Area Name (NAME)'].isin(symmetric_difference.tolist())]

# Drop any columns from df_1 that we do not need for our analysis
# Drop the specified columns
columns_to_drop = ["Year (YEAR)", "Meaning of NAICS code (NAICS2017_LABEL)", "2017 NAICS code (NAICS2017)"]
df_1 = df_1.drop(columns_to_drop, axis=1)

# # Only keep rows where "Meaning of Legal form of organization code (LFO_LABEL)" == "All establishments" and
# # "Meaning of Employment size of establishments code (EMPSZES_LABEL)" == "All establishments"
# df_1 = df_1[(df_1["Meaning of Legal form of organization code (LFO_LABEL)"] == "All establishments") &
#             (df_1["Meaning of Employment size of establishments code (EMPSZES_LABEL)"] == "All establishments")]

# Remove "," from all numeric values in the dataframe
# Loop through each column in the DataFrame
for column in df_1.columns:
    # Remove commas from values
    df_1[column] = df_1[column].str.replace(',', '')


# # Group by "Geographic Area Name (NAME)" and calculate averages
# df_1 = df_1.groupby("Geographic Area Name (NAME)").mean().reset_index()
# # df_1 = df_1.groupby("Geographic Area Name (NAME)")[["Number of establishments (ESTAB)", "Annual payroll ($1,000) (PAYANN)", "First-quarter payroll ($1,000) (PAYQTR1)", "Number of employees (EMP)"]].mean().reset_index()
# # df_1 = df_1.groupby("Geographic Area Name (NAME)")["Number of establishments (ESTAB)"].mean().reset_index()
#
#
# # Rename the new columns
# df_1.rename(columns={
#     "Number of establishments (ESTAB)": "Average #establishments",
#     "Annual payroll ($1,000) (PAYANN)": "Average annual payroll",
#     "First-quarter payroll ($1,000)": "Average first-quarter payroll",
#     "Number of employees (EMP)": "Average #employees"
# }, inplace=True)

# Set the option to display all columns
pd.set_option('display.max_columns', None)
print(df_1.head())

# Set the option to display all columns
pd.set_option('display.max_columns', None)
print(df_1.head())

# Generate the analysis report
report_1 = sv.analyze(df_1)
report_2 = sv.analyze(df_2)

# Display the report in the browser
report_1.show_html('cbp_report.html')
report_2.show_html('bachelor_report.html')


