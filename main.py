import streamlit as st
from polyfuzz import PolyFuzz
import pandas as pd

# Set up the Streamlit app
st.title('Python URL / Redirect Mapping Tool')
st.subheader('Directions:')
st.write(
    '- Upload complete crawl\n'
    '- Upload a list of 404s in CSV format (URL column named URL)\n'
    '- Not recommended for over 10k URLs (very slow)'
)
st.write("Team - [Sarak Dahal](https://www.linkedin.com/in/sarakdahal/)")

# Input fields for URL and file uploads
url = st.text_input('The URL to Match', placeholder='Enter domain (www.google.com)')
file1 = st.file_uploader("Upload Old Crawl CSV File")
file2 = st.file_uploader("Upload New Crawl CSV File")

# Process the uploaded files if both are provided
if file1 is not None and file2 is not None:
    # Read CSV files into DataFrames
    broken = pd.read_csv(file1)
    current = pd.read_csv(file2)
    ROOTDOMAIN = url

    # Convert DataFrames to lists and remove domain from URLs
    broken_list = broken["Address"].tolist()
    broken_list = [sub.replace(ROOTDOMAIN, '') for sub in broken_list]
    current_list = current["Address"].tolist()
    current_list = [sub.replace(ROOTDOMAIN, '') for sub in current_list]

    # Create and run the PolyFuzz model
    model = PolyFuzz("EditDistance")
    model.match(broken_list, current_list)
    df1 = model.get_matches().sort_values(by='Similarity', ascending=False)

    # Filter and format the results
    df1["Similarity"] = df1["Similarity"].round(3)
    df1 = df1[df1['Similarity'] >= 0.857]
    df1["To"] = ROOTDOMAIN + df1["To"]
    df1["From"] = ROOTDOMAIN + df1["From"]

    # Prepare additional data for merging
    df = pd.DataFrame({
        'From Title 1': broken['Title 1'],
        'From Meta Description': broken['Meta Description 1'],
        'From H1-1': broken['H1-1'],
        'To': current['Address'],
        'Title': current['Title 1'],
        'Meta Description': current['Meta Description 1'],
        'H1': current['H1-1']
    })

    # Merge dataframes to create the final output
    df3 = pd.merge(df, df1, on='To')
    df3 = df3[['From Title 1', 'From Meta Description', 'From H1-1', 'Similarity', 'From', 'To', 'Title', 'Meta Description', 'H1']]

    # Display the resulting DataFrame
    st.dataframe(df3)

    # Function to convert DataFrame to CSV
    @st.cache_data
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')

    # Provide a download button for the CSV file
    csv = convert_df(df3)
    st.download_button(
        label="Download Output",
        data=csv,
        file_name="url_mapping.csv",
        mime="text/csv",
        key='download-csv'
    )
