import streamlit as st
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd


st.set_page_config(
    page_title="Store Inventory Manager", page_icon=":bar_chart", layout="wide"
)

st.title(" :bar_chart: Sample Store Inventory Management")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

file_uploader = st.file_uploader(
    ":file_folder: Upload a file ", type=(["csv", "txt", "xlsx"])
)

if file_uploader:
    file_name = file_uploader.name
    st.write(file_name)
    df = pd.read_csv(file_name)
else:
    df = pd.read_csv("Superstore.csv")


col_1, col_2 = st.columns(2)  # Split the display area to two columns
# convert order date column to a datetime field
df["Order Date"] = pd.to_datetime(df["Order Date"], format="%d/%m/%Y")
# df["Order Date"] = df["Order Date"].dt.strftime('%d/%m/%Y')

# Get the earliest and latest date
start_date = pd.to_datetime(df["Order Date"]).min()
end_date = pd.to_datetime(df["Order Date"]).max()

with col_1:
    date_start = pd.to_datetime(st.date_input("Start Date", start_date))
with col_2:
    date_end = pd.to_datetime(st.date_input("End Date", end_date))


df_copy = df[(df["Order Date"] >= date_start) & (df["Order Date"] <= date_end)]

st.sidebar.header("Select filter parameters")

# Get regions
regions = st.sidebar.multiselect("Pick a region", df_copy["Region"].unique())

if not regions:
    df_2 = df_copy.copy()
else:
    df_2 = df[df["Region"].isin(regions)]


# Get states
states = st.sidebar.multiselect("Pick a state", df_2["State"].unique())

if not states:
    df_3 = df_2.copy()
else:
    df_3 = df_2[df_2["State"].isin(states)]


# Get cities
cities = st.sidebar.multiselect("Pick a city", df_3["City"].unique())

# Filter data based on region, state and city

if regions and states is None:
    filtered_df = df_copy
elif states and cities is None:
    filtered_df = df_copy[df_copy["State"].isin(regions)]
elif regions and cities is None:
    filtered_df = df_copy[df_copy["State"].isin(states)]
elif states and cities:
    filtered_df = df_3[df_3["State"].isin(states) & df_3["City"].isin(cities)]
elif regions and cities:
    filtered_df = df_3[df_3["Region"].isin(regions) & df_3["City"].isin(cities)]
elif regions and states:
    filtered_df = df_3[df_3["Region"].isin(regions) & df_3["State"].isin(states)]
elif cities:
    filtered_df = df_3[df_3["City"].isin(cities)]
else:
    filtered_df = df_3[
        df_3["Region"].isin(regions)
        & df_3["State"].isin(states)
        & df_3["City"].isin(cities)
    ]

# Get Categories
category_df = filtered_df.groupby(by=["Category"], as_index=False)["Sales"].sum()

with col_1:
    st.subheader("Category wise Sales")
    fig = px.bar(
        category_df,
        x="Category",
        y="Sales",
        text=["${:,.2f}".format(x) for x in category_df["Sales"]],
        template="seaborn",
    )
    st.plotly_chart(fig, use_container_width=True, height=200)

with col_2:
    st.subheader("Region wise sales")
    fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.5)
    fig.update_traces(text=filtered_df["Region"], textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

cl_1, cl_2 = st.columns(2)

with cl_1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Data",
            data=csv,
            file_name="Category.csv",
            mime="text/csv",
            help="Click here to download the data as a csv file",
        )

with cl_2:
    with st.expander("Region_ViewData"):
        regions = filtered_df.groupby(by="Region", as_index=False)["Sales"].sum()
        st.write(regions.style.background_gradient(cmap="Oranges"))
        csv = regions.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download Data",
            data=csv,
            file_name="Regions.csv",
            mime="text/csv",
            help="Click here to download the data as a csv file",
        )

filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader("Time Series Analysis")


linechart = pd.DataFrame(
    filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()
).reset_index()
fig2 = px.line(
    linechart,
    x="month_year",
    y="Sales",
    labels={"Sales": "Amount"},
    height=500,
    width=1000,
    template="gridon",
)
st.plotly_chart(fig2, use_container_width=True)

with st.expander("View Data of TimeSeries:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Data", data=csv, file_name="TimeSeries.csv", mime="text/csv"
    )


st.subheader(":point_right: Month wise Sub-Category Sales Summary")
with st.expander("Summary_Table"):
    df_sample = df_copy[0:5][
        ["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]
    ]
    fig = ff.create_table(df_sample, colorscale="Cividis")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Month wise Sub-Category Table")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_year = pd.pivot_table(
        data=filtered_df, values="Sales", index=["Sub-Category"], columns="month"
    )
    st.write(sub_category_year.style.background_gradient(cmap="Blues"))
