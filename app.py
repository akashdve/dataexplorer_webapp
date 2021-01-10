import logging
import os
from urllib.request import urlopen
from uuid import uuid4

import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
from PIL import Image

import os

from streamlit import sidebar as side
from matplotlib import pyplot
from py_dotenv import read_dotenv
from wordcloud import STOPWORDS, WordCloud

read_dotenv(".env")

DEFAULT_DATA_SOURCE = "data/val_1k.csv"
TEMP_DIR = os.getenv("TEMP_DIR")
HTML_P_TAG_START = "<p style='text-align: center;'>"
HTML_P_TAG_END = "</p>"
HTML_BREAK = "<br>"
HTML_BOLD_START = "<b>"
HTML_BOLD_END = "</b>"
hide_streamlit_style = "<style>#MainMenu {visibility: hidden;}footer {visibility: hidden;}</style>"

WORDCLOUD_OBJ = WordCloud(width=800, height=800,
                          background_color='white',
                          stopwords=STOPWORDS, min_font_size=10)

STOPWORDS_SET = set(STOPWORDS)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def about_me():
    side.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">',
                unsafe_allow_html=True)
    side.image(Image.open(urlopen("https://avatars2.githubusercontent.com/u/34905288?s=400&u=c52b3b2744adf04a26a742000fa83a5c1ea5f92d&v=4")),
                     width=200)

    side.subheader("Akash Dave")
    side.markdown("Hi! I am in superlove with data and I do magic using Python. Relax Guys! I am not saying Java is bad.")

    side.markdown('<a href="https://github.com/akashdve"><i class="fa fa-github" style="font-size:48px;"></i></a>',
                   unsafe_allow_html=True)


def get_temp_path(filename: str) -> str:
    filename = str(uuid4()) + "_" + str(filename)
    return os.path.join(TEMP_DIR, filename)


@st.cache(persist=True)
def load_data_from_source(source) -> pd.DataFrame:
    func = pd.read_csv
    if str(source).endswith(".xlsx"):
        func = pd.read_excel
    elif str(source).endswith(".json"):
        func = pd.read_json
    elif str(source).endswith(".df"):
        func = pd.read_feather

    try:
        if source:
            print(("running if part"))
            df = func(source)
        else:
            print("Running else part ---- func {}".format(func))
            df = func(DEFAULT_DATA_SOURCE)
        return df
    except Exception as e:
        logger.error("Error in loading data from source: {}".format(e))
        return pd.DataFrame([])


def clean_text(text):
    text = str(text).lower()
    return text


def show_wordcloud(main_df: pd.DataFrame):
    try:
        nonnumeric_cols = main_df.select_dtypes(exclude=['int16', 'int32', 'int64', 'float16', 'float32', 'float64']).columns
        selected_nonnumeric_cols = st.multiselect("Select columns to view insights", nonnumeric_cols.tolist(), nonnumeric_cols[0])
        nonnumeric_col_divs = st.beta_columns(len(selected_nonnumeric_cols))
        for i, col in enumerate(selected_nonnumeric_cols):
            with nonnumeric_col_divs[i]:
                st.subheader(col)
                with st.spinner("Forming cloud..."):
                    series = main_df[col].map(clean_text)
                    joined_text = " ".join(series)
                    wordcloud_temp_path = get_temp_path("wordcloud.png")
                    WORDCLOUD_OBJ.generate(joined_text).to_file(wordcloud_temp_path)
                    st.image(Image.open(wordcloud_temp_path), use_column_width=True)
    except Exception as e:
        st.error("Something went wrong!")
        logger.error(e)


def show_column_insights(main_df: pd.DataFrame):
    selected_cols = st.multiselect("Select columns to view insights", main_df.columns.tolist(), main_df.columns[0])
    try:
        selected_col_divs = st.beta_columns(len(selected_cols))
        for i, col in enumerate(selected_cols):
            with selected_col_divs[i]:
                st.subheader(col)
                st.dataframe(main_df[col].describe())
    except:
        st.warning("Please select atleast one column to view insights")


def main():

    ###########################################################
    st.set_page_config(page_title="Handy Data Explorer App")
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    st.title("Handy Data Explorer App")
    st.markdown("Wanna know what your data mean?")
    side.markdown("<button type='button' class='btn btn-primary'>Note:</button> More features coming soon",
                  unsafe_allow_html=True)
    side.markdown("This webapp is developed under DOHackathon.")
    side.markdown("Why so simple?")
    side.markdown("This is the very first version. I came to know about this hackathon just one day before the deadline. Having very little time to think, pick and implement"
                  " an idea, I hacked myself to the fullest and explored my new limits.")
    side.header("About Me")
    about_me()
    ###########################################################

    source = st.text_input("Enter the source of the dataset")
    st.markdown(HTML_P_TAG_START+"OR"+HTML_P_TAG_END, unsafe_allow_html=True)
    file = st.file_uploader("Upload a file (.csv, .xlsx, .json, .df)")

    if source and file:
        st.warning("Please select either source or upload a file")


    main_df = load_data_from_source(source=file if file else source)
    # numeric_cols = main_df.select_dtypes(include=['int16', 'int32', 'int64', 'float16', 'float32', 'float64']).columns

    st.markdown("<hr>",unsafe_allow_html=True)
    st.header("Data Insights")
    st.markdown("<hr>", unsafe_allow_html=True)
    if not (source and file): st.info("using example dataset (Taken from Amazon product reviews dataset)")
    st.dataframe(main_df.head())

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(HTML_BREAK + HTML_P_TAG_START + HTML_BOLD_START + "Heatmap (for numeric columns)" + HTML_BOLD_END + HTML_P_TAG_END, unsafe_allow_html=True)
    fig = sns.heatmap(main_df.corr(), annot=True).get_figure()
    heatmap_temp_path = get_temp_path("heatmap.png")
    fig.savefig(heatmap_temp_path)
    st.image(Image.open(heatmap_temp_path))

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(HTML_BREAK + HTML_P_TAG_START + HTML_BOLD_START + "Pair Plots (for numeric columns)" + HTML_BOLD_END + HTML_P_TAG_END,
                unsafe_allow_html=True)
    pairplot_temp_path = get_temp_path("pairplot.png")
    sns.pairplot(main_df).savefig(pairplot_temp_path)
    st.image(Image.open(pairplot_temp_path))

    st.markdown("<hr>", unsafe_allow_html=True)

    st.header("Min/Max/Count/Freq")
    show_column_insights(main_df)

    st.markdown("<hr>", unsafe_allow_html=True)

    st.header("Wordcloud of non-numeric columns")
    show_wordcloud(main_df)




if __name__ == '__main__':
    main()