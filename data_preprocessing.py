import pandas as pd
import sweetviz as sv

# Load the dataset (example: iris dataset)
df_1 = pd.read_csv('datasets/CBP2019.CB1900CBP-2023-05-14T012245.csv')
df_2 = pd.read_csv('datasets/Bachelor_Degree_Majors.csv')
df_3 = pd.read_csv('datasets/state_regions.csv')

# Drop any columns from df_1 that we do not need for our analysis
columns_to_drop = ["Year (YEAR)", "Meaning of NAICS code (NAICS2017_LABEL)", "2017 NAICS code (NAICS2017)",
                   "Meaning of Legal form of organization code (LFO_LABEL)"]
df_1 = df_1.drop(columns_to_drop, axis=1)


# Since we dropped some columns, some rows have become duplicates of others. Thus, we proceed to drop them.
df_1 = df_1.drop_duplicates()


# Rename the columns of df_1 to make them easier to work with
column_rename_mapping = {
    "Geographic Area Name (NAME)": "State",
    "Meaning of Employment size of establishments code (EMPSZES_LABEL)": "Business size",
    "Number of establishments (ESTAB)": "Average #establishments",
    "Annual payroll ($1,000) (PAYANN)": "Average annual payroll",
    "First-quarter payroll ($1,000) (PAYQTR1)": "Average first-quarter payroll",
    "Number of employees (EMP)": "Average #employees"
}
df_1.rename(columns=column_rename_mapping, inplace=True)


# For the CPB dataset (df_1), drop any rows where "Business size" == "All establishments"
df_1 = df_1[(df_1["Business size"] != "All establishments")]


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


# Get the non-common values between the "State" columns of the 2 datasets (df_1 and df_2)
symmetric_difference = pd.Series(list(set(df_1['State']).symmetric_difference(set(df_2['State']))))
print("\n> States included in CBP but not in Bachelor Majors dataset: {}".format(len(symmetric_difference)))
print(symmetric_difference)


# We will to drop the rows in df_1 and df_2 that contain any of the non-common (State) values.
df_1 = df_1[~df_1['State'].isin(symmetric_difference.tolist())]
df_2 = df_2[~df_2['State'].isin(symmetric_difference.tolist())]


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

# Convert df_1 number columns to numeric values
numeric_columns = ["Average #establishments", "Average annual payroll", "Average first-quarter payroll",
                   "Average #employees"]
df_1[numeric_columns] = df_1[numeric_columns].apply(pd.to_numeric)

# Convert df_2 number columns to numeric values
numeric_columns = ["Bachelor's Degree Holders", "Science and Engineering", "Science and Engineering Related Fields",
                   "Business", "Education", "Arts, Humanities and Others"]
df_2[numeric_columns] = df_2[numeric_columns].apply(pd.to_numeric)


# ================================== Data Exchange ====================================
# ====== Add the information from the "State Regions" dataset (df_3) to CBP (df_1) as a new column
df_1 = pd.merge(df_1, df_3, on='State', how='left')
df_1 = pd.merge(df_1, df_3, on='State', how='left')

# ====== Generate a new "Men to Women Ratio" column in df_1 that contains the men to women
# bachelor holders ratio for each state
# Filter the DataFrame for "Male" and "Female" separately
male_df = df_2[df_2['Sex'] == 'Male']
female_df = df_2[df_2['Sex'] == 'Female']

# Group by "State" and calculate the sum of "Bachelor's Degree Holders" for each gender
male_counts = male_df.groupby('State')['Bachelor\'s Degree Holders'].sum()
female_counts = female_df.groupby('State')['Bachelor\'s Degree Holders'].sum()

# Calculate the ratio of men to women for each state
ratio = male_counts / female_counts

# Create a new column in df_1 and map the men/women ratios there based on the "State" value of each entry.
df_1['Men to women ratio'] = df_1['State'].map(ratio)


# ====== Determine the field that has the largest and second-largest number of graduates per State
# Filter the dataset to keep only rows where "Sex" is equal to "Total"
filtered_df = df_2[df_2["Sex"] == "Total"]

# Group the filtered DataFrame by "State"
grouped_df = filtered_df.groupby("State")

# Create an empty dictionary to store the results
state_column_dict = {}


# ==== Determine the most popular field of studies
# Iterate over each distinct value of "State"
for state, group in grouped_df:
    # Calculate the summed values for each column
    summed_values = group[["Science and Engineering", "Science and Engineering Related Fields", "Business", "Education",
                           "Arts, Humanities and Others"]].sum()

    # Find the column with the highest summed value
    max_column = summed_values.idxmax()

    # Save the column name to the state:column dictionary
    state_column_dict[state] = max_column

# Add the new column to the df_2 dataframe
df_1["Most popular degree field"] = df_1["State"].map(state_column_dict)

# ==== Determine the 2nd most popular field of studies
# Iterate over each distinct value of "State"
for state, group in grouped_df:
    # Calculate the summed values for each column
    summed_values = group[["Science and Engineering", "Science and Engineering Related Fields", "Business", "Education",
                           "Arts, Humanities and Others"]].sum()

    # Sort the summed values in descending order and get the column name with the second largest summed value
    second_largest_column = summed_values.sort_values(ascending=False).index[1]

    # Save the column name to the state:column dictionary
    state_column_dict[state] = second_largest_column

# Add the new column to the df_2 dataframe
df_1["2nd Most popular degree field"] = df_1["State"].map(state_column_dict)

# # Display the updated df_1 dataframe
# print("len 2: ", len(state_column_dict))
# for key, value in state_column_dict.items():
#     print(key + ":" + value)
# print(df_1)
#
# # Specify the columns to be printed
# columns_to_print = ["Most Popular Degree Field", "2nd Most Popular Degree Field"]
#
# # Print all rows of specified columns
# print(df_1[columns_to_print])

# ====== Add a new "#(Mid)Senior graduates" column to df_1 that is generated by summing the "25-39" and "40-64"
# age groups of the "Bachelor's" dataset (df_2) for every State. NOTE: These age groups are considered to include both
# sexes ("Total" value of the "Sex" attribute).
# Filter the dataset to keep only rows where "Sex" is equal to "Total"
filtered_df = df_2[df_2["Sex"] == "Total"]

# Group the filtered DataFrame by "State"
grouped_df = filtered_df.groupby("State")

# Create an empty dictionary to store the results
state_sum_dict = {}

# Iterate over each distinct value of "State"
for state, group in grouped_df:
    # Filter the group based on the specified conditions and calculate the sum of "Bachelor's Degree Holders"
    age_group_condition = (group["Age Group"].isin(["25 to 39", "40 to 64"]))
    sum_value = group.loc[age_group_condition, "Bachelor's Degree Holders"].sum()

    # Save the sum to the state:sum dictionary
    state_sum_dict[state] = sum_value

df_1["#(Mid)Senior graduates"] = df_1["State"].map(state_sum_dict)
# ============================================================================

# For the Bachelor's dataset (df_2), drop any rows where "Sex" == "Total"
df_2 = df_2[(df_2["Sex"] != "Total")]


# Generate the analysis report
report_1 = sv.analyze(df_1)
report_2 = sv.analyze(df_2)

# Display the report in the browser
report_1.show_html('cbp_report.html')
report_2.show_html('bachelor_report.html')

print("> Saving preprocessed datasets to .csv files...")
df_1.to_csv('datasets/CBP_preprocessed.csv', index=False)
df_2.to_csv('datasets/Bachelor_preprocessed.csv', index=False)

