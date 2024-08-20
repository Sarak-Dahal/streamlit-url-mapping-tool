import streamlit as st
from polyfuzz import PolyFuzz
import pandas as pd

st.title('Python URL / Redirect Mapping Tool')
st.subheader('Directions:')
st.write('- Upload complete crawl \n - Upload a list of 404s in.CSV format (URL column named URL) \n - Would not '
         'recommend with over 10k URLs (very slow)')
st.write("Author - [Venkata Pagadala](https://www.linkedin.com/in/venkata-pagadala/)")
st.write("Team - [Sarak Dahal](https://www.linkedin.com/in/sarakdahal/)")
# Importing the URL CSV files
url = st.text_input('The URL to Match', placeholder='Enter domain (www.google.com)')
file1 = st.file_uploader("Upload Old Crawl CSV File")
file2 = st.file_uploader("Upload New Crawl CSV File")
if file1 is not None and file2 is not None:
    broken = pd.read_csv(file1)
    current = pd.read_csv(file2)
    ROOTDOMAIN = url
    # Converting DF to List
    broken_list = broken["Address"].tolist()
    broken_list = [sub.replace(ROOTDOMAIN, '') for sub in broken_list]
    current_list = current["Address"].tolist()
    current_list = [sub.replace(ROOTDOMAIN, '') for sub in current_list]
    # Creating the Polyfuzz model
    model = PolyFuzz("EditDistance")
    model.match(broken_list, current_list)
    df1 = model.get_matches()
    df1 = df1.sort_values(by='Similarity', ascending=False)
    # Polishing and Pruning
    df1["Similarity"] = df1["Similarity"].round(3)
    df1 = df1.sort_values(by='Similarity', ascending=False)
    index_names = df1.loc[df1['Similarity'] < .857].index
    amt_dropped = len(index_names)
    df1.drop(index_names, inplace=True)
    df1["To"] = ROOTDOMAIN + df1["To"]
    df1["From"] = ROOTDOMAIN + df1["From"]
    # df1
    df = pd.DataFrame()
    df['From Title 1'] = broken['Title 1']
    df['From Meta Description'] = broken['Meta Description 1']
    df['From H1-1'] = broken['H1-1']
    df['To'] = current['Address']
    df['Title'] = current['Title 1']
    df['Meta Description'] = current['Meta Description 1']
    df['H1'] = current['H1-1']
    # df
    df3 = pd.merge(df,df1,on='To')
    df3 = df3[['From Title 1','From Meta Description','From H1-1','Similarity','From','To', 'Title', 'Meta Description', 'H1']]
    df3
    # Downloading of File
    @st.cache
    def convert_df(df3):
        return df3.to_csv().encode('utf-8')
    csv = convert_df(df3)
    st.download_button(
        "Download Output",
        csv,
        "file.csv",
        "text/csv",
        key='download-csv'
    )