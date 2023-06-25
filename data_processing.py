import pandas as pd
import sweetviz as sv

# Load the dataset (example: iris dataset)
cbp_df = pd.read_csv('datasets/sources/CBP2019.CB1900CBP-2023-05-14T012245.csv')
bachelor_df = pd.read_csv('datasets/sources/Bachelor_Degree_Majors.csv')
sr_df = pd.read_csv('datasets/sources/state_regions.csv')

# For cbp_df, we will not be using the "Meaning of Legal form of organization code (LFO_LABEL)" for our analysis.
# Thus, we proceed to filter cbp_df, so that only the rows where this attribute equals "All establishments" are kept
cbp_df = cbp_df[(cbp_df["Meaning of Legal form of organization code (LFO_LABEL)"] == "All establishments")]

# Drop any columns from cbp_df that we do not need for our analysis
columns_to_drop = [
                   "Year (YEAR)",
                   "Meaning of NAICS code (NAICS2017_LABEL)",
                   "2017 NAICS code (NAICS2017)",
                   "Annual payroll ($1,000) (PAYANN)",
                   "First-quarter payroll ($1,000) (PAYQTR1)",
                   "Meaning of Legal form of organization code (LFO_LABEL)"
                   ]

cbp_df = cbp_df.drop(columns_to_drop, axis=1)

# Since we dropped some columns, some rows have become duplicates of others. Thus, we proceed to drop them.
cbp_df = cbp_df.drop_duplicates()

# Rename the columns of cbp_df to make them easier to work with
column_rename_mapping = {
    "Geographic Area Name (NAME)": "State",
    "Meaning of Employment size of establishments code (EMPSZES_LABEL)": "Business size",
    "Number of establishments (ESTAB)": "#Establishments",
    # "Annual payroll ($1,000) (PAYANN)": "Average annual payroll",
    # "First-quarter payroll ($1,000) (PAYQTR1)": "Average first-quarter payroll",
    "Number of employees (EMP)": "Total #employees"
}
cbp_df.rename(columns=column_rename_mapping, inplace=True)

# Contradiction mitigation: For the CPB dataset (cbp_df), drop any rows where "Business size" == "All establishments"
cbp_df = cbp_df[(cbp_df["Business size"] != "All establishments")]


# For the CPB dataset (cbp_df), only keep the rows where the value of the "Business size" attribute refers to a company
# that represents a "major" competitor, according to our client's criteria
values_to_keep = [
    "Establishments with 50 to 99 employees",
    "Establishments with 100 to 249 employees",
    "Establishments with 250 to 499 employees",
    "Establishments with 500 to 999 employees",
    "Establishments with 1,000 employees or more"
]
cbp_df = cbp_df[cbp_df["Business size"].isin(values_to_keep)]

# Get the non-common values between the "State" columns of the 2 datasets (cbp_df and bachelor_df)
symmetric_difference = pd.Series(list(set(cbp_df['State']).symmetric_difference(set(bachelor_df['State']))))
print("\n> States included in CBP but not in Bachelor Majors dataset: {}".format(len(symmetric_difference)))
print(symmetric_difference)

# We will to drop the rows in cbp_df and bachelor_df that contain any of the non-common (State) values.
cbp_df = cbp_df[~cbp_df['State'].isin(symmetric_difference.tolist())]
bachelor_df = bachelor_df[~bachelor_df['State'].isin(symmetric_difference.tolist())]

# Remove "," from all numeric values in the CPB dataframe
# Loop through each column in the DataFrame
for column in cbp_df.columns:
    # Remove commas from values
    cbp_df[column] = cbp_df[column].str.replace(',', '')

# Remove "," from all numeric values in the Bachelor's dataframe
# Loop through each column in the DataFrame
for column in bachelor_df.columns:
    # Remove commas from values
    bachelor_df[column] = bachelor_df[column].str.replace(',', '')

# Convert cbp_df number columns to numeric values
numeric_columns = [
                   "#Establishments",
                   # "Average annual payroll",
                   # "Average first-quarter payroll",
                   "Total #employees"
                  ]
cbp_df[numeric_columns] = cbp_df[numeric_columns].apply(pd.to_numeric)

# Convert bachelor_df number columns to numeric values
numeric_columns = ["Bachelor's Degree Holders", "Science and Engineering", "Science and Engineering Related Fields",
                   "Business", "Education", "Arts, Humanities and Others"]
bachelor_df[numeric_columns] = bachelor_df[numeric_columns].apply(pd.to_numeric)

# Add the information from the "State Regions" dataset (sr_df) to CBP (cbp_df) as a new column
cbp_df = pd.merge(cbp_df, sr_df, on='State', how='left')

# ====== Generate a new "Men to women degree holders ratio" column in cbp_df that contains the men to women
# bachelor holders ratio for each state
# Filter the DataFrame for "Male" and "Female" separately
male_df = bachelor_df[bachelor_df['Sex'] == 'Male']
female_df = bachelor_df[bachelor_df['Sex'] == 'Female']

# Group by "State" and calculate the sum of "Bachelor's Degree Holders" for each gender
male_counts = male_df.groupby('State')['Bachelor\'s Degree Holders'].sum()
female_counts = female_df.groupby('State')['Bachelor\'s Degree Holders'].sum()

# Calculate the ratio of men to women degree holdersfor each state
ratio = male_counts / female_counts

# Create a new column in cbp_df and map the men/women ratios there based on the "State" value of each entry.
cbp_df['Men to women degree holders ratio'] = cbp_df['State'].map(ratio)


# Filter the dataset to keep only rows where "Sex" is equal to "Total" and "Age Group" is equal to "25 and older"
filtered_bachelor_df = bachelor_df[(bachelor_df["Sex"] == "Total") & (bachelor_df["Age Group"] == "25 and older")]

# Merge the cbf and bachelor's datasets, keeping only selected columns of bachelor's df
cbp_df = pd.merge(cbp_df, filtered_bachelor_df[['State', 'Bachelor\'s Degree Holders', 'Science and Engineering',
                                           'Science and Engineering Related Fields',
                                           'Business', 'Education', 'Arts, Humanities and Others']],
                  on='State', how='left')

# ====== Add a new "#(Mid)Senior degree holders" column to cbp_df that is generated by summing the values of
# "Bachelor's Degree Holders" for the "25-39" and "40-64" age groups of the "Bachelor's"
# dataset (bachelor_df) for every State.
# NOTE: These age groups are considered to include both sexes ("Total" value of the "Sex" attribute).
# Filter the dataset to keep only rows where "Sex" is equal to "Total"
filtered_df = bachelor_df[bachelor_df["Sex"] == "Total"]

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

cbp_df["#(Mid)Senior degree holders"] = cbp_df["State"].map(state_sum_dict)

# ====== Add a new "(Mid)Senior to total ratio" column to cbp_df that is defined per State as:
# #(Mid)Senior degree holders/Bachelor's Degree Holders
# Group the bachelor_df DataFrame by "State" and filter rows where "Sex" is "Total"
filtered_grouped_df = bachelor_df[(bachelor_df['Sex'] == 'Total') & (bachelor_df["Age Group"] == "25 and older")].groupby("State")

# Sum the values of "Bachelor's Degree Holders" per state
degree_holders_per_state = filtered_grouped_df['Bachelor\'s Degree Holders'].first()

# Group the cbp_df DataFrame by "State"
grouped_df = cbp_df.groupby("State")

# Sum the values of "#(Mid)Senior degree holders" per state
midsenior_holders_per_state = grouped_df['#(Mid)Senior degree holders'].first()

# Calculate the ratio
ratio = midsenior_holders_per_state / degree_holders_per_state


# Create a new column in cbp_df and map the #Degree Holders/#Business establishments ratios there,
# based on the "State" value of each entry.
cbp_df["(Mid)Senior to total ratio"] = cbp_df['State'].map(ratio)


# ====== Generate a new "Degree holders to establishments ratio" column that holds the
# #Degree Holders/#Business establishments ratio per State, taking into consideration both sexes.
# Group the bachelor_df DataFrame by "State" and filter rows where "Sex" is "Total"
filtered_df = bachelor_df[bachelor_df['Sex'] == 'Total'].groupby('State')

# Sum the values of "Bachelor's Degree Holders" per state
degree_holders_per_state = filtered_df['Bachelor\'s Degree Holders'].sum()

# Group the cbp_df DataFrame by "State"
grouped_df = cbp_df.groupby("State")

# Sum the values of "Business size" per State
establishments_per_state = grouped_df["#Establishments"].sum()

# Calculate the ratio
ratio = degree_holders_per_state / establishments_per_state

# Create a new column in cbp_df and map the #Degree Holders/#Business establishments ratios there,
# based on the "State" value of each entry.
cbp_df['Degree holders to establishments ratio'] = cbp_df['State'].map(ratio)

# Rename certain columns so that the new names properly reflect their meaning
column_rename_mapping = {
    "Bachelor's Degree Holders": "#Bachelor's degree holders",
    "Science and Engineering": "#Science and Engineering degree holders",
    "Science and Engineering Related Fields": "#Science and Engineering Related Fields degree holders",
    "Business": "#Business degree holders",
    "Education": "#Education degree holders",
    "Arts, Humanities and Others": "#Arts, Humanities and Others degree holders"
}
cbp_df.rename(columns=column_rename_mapping, inplace=True)


# ====================== Adding Extra datasets (other than those provided by the client) =====================
universities = pd.read_csv('datasets/sources/National Universities Rankings.csv')
business = pd.read_csv('datasets/sources/BDSTIMESERIES.BDSGEO-2023-05-31T192640.csv')
pd.set_option('display.max_columns', None)

#===== Add dataset with states abbreviations to work with universities ranking
states = pd.read_csv('datasets/sources/state_names.csv')

universities['State Abbr'] = universities['Location'].str[-2:]

merged = pd.merge(universities, states, left_on='State Abbr', right_on='Alpha code')

# Add full state name
universities['State'] = merged['State']

# Rename the columns of business to make them easier to work with
column_rename_mapping = {
    "Geographic Area Name (NAME)": "State",
    "Year (YEAR)": "Year",
    "Rate of establishments born during the last 12 months (ESTABS_ENTRY_RATE)": "Rate establishments born",
    "Rate of establishments exited during the last 12 months (ESTABS_EXIT_RATE)": "Rate establishments exited",
}
business.rename(columns=column_rename_mapping, inplace=True)

# Get the non-common values between the "State" columns of the 2 datasets (cbp_df and universities)
symmetric_difference = pd.Series(list(set(universities['State']).symmetric_difference(set(cbp_df['State']))))
print("\n> States included in Universities but not in CBP dataset: {}".format(len(symmetric_difference)))
print(symmetric_difference)

# We will to drop the rows in universities that contain any of the non-common (State) values.
universities = universities[~universities['State'].isin(symmetric_difference.tolist())]

# Get the non-common values between the "State" columns of the 2 datasets (cbp_df and business)
symmetric_difference = pd.Series(list(set(business['State']).symmetric_difference(set(cbp_df['State']))))
print("\n> States included in Business Dynamics but not in CBP dataset: {}".format(len(symmetric_difference)))
print(symmetric_difference)

# We will to drop the rows in business_agg that contain any of the non-common (State) values.
business = business[~business['State'].isin(symmetric_difference.tolist())]


# ====== Generate a new "Rate born - exited" column that holds the difference between number of businesses born and
# the number of businesses exited per state over the last decade
business = business[['State', 'Year', "Rate establishments born", "Rate establishments exited"]]
# Select the data for the last decade
business_recent = business[(business['Year'] >= 2009) & (business['Year'] <= 2019)]

# Calculate average rates for the last decade
business_agg = business_recent.groupby('State')[['Rate establishments born', 'Rate establishments exited']].mean()
business_agg.reset_index(inplace=True)

# Calculate the difference between born and exited rate (kind of "clean" born rate)
# If negative: more exited than born
business_agg['Rate born - exited'] = business_agg['Rate establishments born'] - business_agg[
    'Rate establishments exited']


# Select necessary columns from universities df
universities = universities[['Name', 'Rank', 'State']]

universities_agg = universities.groupby('State')[['Rank']].mean()
universities_agg.rename(columns={"Rank": "Average rank"}, inplace=True)
print(universities_agg)


# Join business dynamics and universities datasets
final_extra = pd.merge(business_agg, universities_agg, on='State')

# Output the dataframe formed using the "extra" datasets as a .csv file
final_extra.to_csv('datasets/generated/extra_datasets_preprocessed.csv', index=False)

# Merge cbp_df and final_extra on "State"
final_dataset = pd.merge(cbp_df, final_extra, on='State', how='left')


# ====== Generate a new "Average #employees" attribute
final_dataset['Average #employees'] = final_dataset['Total #employees'] / final_dataset['#Establishments']

# Add a new "State code" column to all rows, that contains the 2-letter Alpha Code which of each State
# Merge cbp_df and states_df based on the "State" column
states_df = pd.read_csv('datasets/sources/state_names.csv')
merged_df = pd.merge(final_dataset, states_df, on="State", how="left")

# Create a new column "State code" in cbp_df containing the matched "Alpha code" values
final_dataset["State code"] = merged_df["Alpha code"]

# Drop any attributes from final_dataset that are determined to be irrelevant for our analysis
drop_column_names = ["Rate establishments born", "Rate establishments exited"]

final_dataset = final_dataset.drop(columns=drop_column_names)


# ==================== Display and export dataframe ====================
# print final_dataset in the terminal using markdown
print(final_dataset.to_markdown())

# Generate the analysis report
report_1 = sv.analyze(final_dataset)

# Display the report in the browser
report_1.show_html('final_report.html')

print("> Saving preprocessed datasets to .csv files...")
final_dataset.to_csv('datasets/generated/final_preprocessed.csv', index=False)
