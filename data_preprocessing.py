import pandas as pd
import sweetviz as sv

# Load the dataset (example: iris dataset)
df_1 = pd.read_csv('datasets/CBP2019.CB1900CBP-2023-05-14T012245.csv')
df_2 = pd.read_csv('datasets/Bachelor_Degree_Majors.csv')


# Drop any columns from df_1 that we do not need for our analysis
columns_to_drop = ["Year (YEAR)", "Meaning of NAICS code (NAICS2017_LABEL)", "2017 NAICS code (NAICS2017)",
                   "Meaning of Legal form of organization code (LFO_LABEL)"]
df_1 = df_1.drop(columns_to_drop, axis=1)


# Rename the columns of df_1 to make them easier to work with
column_rename_mapping = {
    "Geographic Area Name (NAME)": "State",
    "Meaning of Employment size of establishments code (EMPSZES_LABEL)": "Business size"
}
df_1.rename(columns=column_rename_mapping, inplace=True)


# For the CPB dataset (df_1), drop any rows where "Business size" == "All establishments"
df_1 = df_1[(df_1["Business size"] != "All establishments")]


# Remove "," from all numeric values in the CPB dataframe
# Loop through each column in the DataFrame
for column in df_1.columns:
    # Remove commas from values
    df_1[column] = df_1[column].str.replace(',', '')


# Remove "," from all numeric values in the Bachelor's dataframe
# Loop through each column in the DataFrame
for column in df_2.columns:
    # Remove commas from values
    df_2[column] = df_2[column].str.replace(',', '')


# Convert df_2 number columns to numeric values
numeric_columns = ["Bachelor's Degree Holders", "Science and Engineering", "Science and Engineering Related Fields",
                   "Business", "Education", "Arts, Humanities and Others"]
df_2[numeric_columns] = df_2[numeric_columns].apply(pd.to_numeric)


# Generate a new "Men to Women Ratio" column that contains the men to women bachelor holders ratio for each state
# Filter the DataFrame for "Male" and "Female" separately
male_df = df_2[df_2['Sex'] == 'Male']
female_df = df_2[df_2['Sex'] == 'Female']

# Group by "State" and calculate the sum of "Bachelor's Degree Holders" for each gender
male_counts = male_df.groupby('State')['Bachelor\'s Degree Holders'].sum()
female_counts = female_df.groupby('State')['Bachelor\'s Degree Holders'].sum()

# Calculate the ratio of men to women for each state
ratio = male_counts / female_counts

# # Print the resulting ratio
# print(ratio)

df_2['Men to Women Ratio'] = df_2['State'].map(ratio)


# For the Bachelor's dataset (df_2), drop any rows where "Sex" == "Total"
df_2 = df_2[(df_2["Sex"] != "Total")]


# Get the common values between the two columns
common_values = pd.Series(list(set(df_1['State']).intersection(set(df_2['State']))))
print("\n> States included both in CBP and in Bachelor Majors dataset: {}".format(len(common_values)))
print(common_values)


# Get the non-common values between the two columns
symmetric_difference = pd.Series(list(set(df_1['State']).symmetric_difference(set(df_2['State']))))
print("\n> States included in CBP but not in Bachelor Majors dataset: {}".format(len(symmetric_difference)))
print(symmetric_difference)


# We will to drop the rows in df_1 that contain any of the non-common (State) values.
# Drop rows containing the specified values
df_1 = df_1[~df_1['State'].isin(symmetric_difference.tolist())]


# For the CPB dataset (df_1), only keep the rows where the value of the "Business size" attribute refers to a company
# that represents a "major" competitor, according to our client's criteria
values_to_keep = [
    "Establishments with 50 to 99 employees",
    "Establishments with 100 to 249 employees",
    "Establishments with 250 to 499 employees",
    "Establishments with 500 to 999 employees",
    "Establishments with 1,000 employees or more"
]
df_1 = df_1[df_1["Business size"].isin(values_to_keep)]


# Use CBP as the main dataset
# Add new attributes per State using data from the bachelor's dataset:
# - Sex: Male/Female graduates ratio
# -

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

print(df_2.columns)

# Generate the analysis report
report_1 = sv.analyze(df_1)
report_2 = sv.analyze(df_2)

# Display the report in the browser
report_1.show_html('cbp_report.html')
report_2.show_html('bachelor_report.html')


