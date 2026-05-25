import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# Load dataset
df = pd.read_csv("used_car_listings.csv")

# Basic cleaning
df["price"] = pd.to_numeric(df["price"], errors="coerce")
df["mileage"] = pd.to_numeric(df["mileage"], errors="coerce")
df["year"] = pd.to_numeric(df["year"], errors="coerce")

required_cols = ["price", "mileage", "year", "make", "model", "location"]
df = df.dropna(subset=required_cols)

# Create useful columns
df["year"] = df["year"].astype(int)
df["car_age"] = 2026 - df["year"]
df["make_model"] = df["make"].astype(str) + " " + df["model"].astype(str)

# Pull country from location column.
# Example: "New Lindsey, GA, US" -> "US"
df["country"] = df["location"].astype(str).str.split(",").str[-1].str.strip()
df["country"] = df["country"].replace({"": "Unknown", "nan": "Unknown"})

# Make sure optional text columns do not break filters/charts
for col in ["fuel_type", "seller_type", "condition", "transmission", "body_type"]:
    if col in df.columns:
        df[col] = df[col].fillna("Unknown").astype(str)


# Dropdown values
makes = sorted(df["make"].dropna().unique())
fuel_types = sorted(df["fuel_type"].dropna().unique())
seller_types = sorted(df["seller_type"].dropna().unique())
conditions = sorted(df["condition"].dropna().unique())
countries = sorted(df["country"].dropna().unique())

min_year, max_year = int(df["year"].min()), int(df["year"].max())
min_price, max_price = int(df["price"].min()), int(df["price"].max())

if max_year > min_year:
    year_step = max(1, (max_year - min_year) // 6)
else:
    year_step = 1

year_marks = {y: str(y) for y in range(min_year, max_year + 1, year_step)}
year_marks[min_year] = str(min_year)
year_marks[max_year] = str(max_year)


# App setup
app = Dash(__name__)
server = app.server

CARD_STYLE = {
    "backgroundColor": "white",
    "padding": "18px",
    "borderRadius": "14px",
    "boxShadow": "0 2px 10px rgba(0,0,0,0.06)",
}

app.layout = html.Div(
    style={
        "fontFamily": "Arial, sans-serif",
        "backgroundColor": "#f6f8fb",
        "padding": "24px",
    },
    children=[
        html.Div(
            style={"maxWidth": "1250px", "margin": "0 auto"},
            children=[
                html.H1("Used Car Listings Dashboard", style={"marginBottom": "4px"}),
                html.P(
                    "Explore pricing, mileage, vehicle age, make/model trends, seller type, and country differences.",
                    style={"color": "#555", "marginTop": "0"},
                ),

                html.Div(
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "repeat(4, minmax(180px, 1fr))",
                        "gap": "14px",
                        "backgroundColor": "white",
                        "padding": "18px",
                        "borderRadius": "14px",
                        "boxShadow": "0 2px 10px rgba(0,0,0,0.06)",
                        "marginBottom": "18px",
                    },
                    children=[
                        html.Div([
                            html.Label("Make"),
                            dcc.Dropdown(
                                id="make-filter",
                                options=[{"label": m, "value": m} for m in makes],
                                value=[],
                                multi=True,
                                placeholder="All makes",
                            ),
                        ]),
                        html.Div([
                            html.Label("Country"),
                            dcc.Dropdown(
                                id="country-filter",
                                options=[{"label": c, "value": c} for c in countries],
                                value=[],
                                multi=True,
                                placeholder="All countries",
                            ),
                        ]),
                        html.Div([
                            html.Label("Fuel Type"),
                            dcc.Dropdown(
                                id="fuel-filter",
                                options=[{"label": f, "value": f} for f in fuel_types],
                                value=[],
                                multi=True,
                                placeholder="All fuel types",
                            ),
                        ]),
                        html.Div([
                            html.Label("Seller Type"),
                            dcc.Dropdown(
                                id="seller-filter",
                                options=[{"label": s, "value": s} for s in seller_types],
                                value=[],
                                multi=True,
                                placeholder="All seller types",
                            ),
                        ]),
                        html.Div([
                            html.Label("Condition"),
                            dcc.Dropdown(
                                id="condition-filter",
                                options=[{"label": c.title(), "value": c} for c in conditions],
                                value=[],
                                multi=True,
                                placeholder="All conditions",
                            ),
                        ]),
                        html.Div(style={"gridColumn": "span 3"}, children=[
                            html.Label("Year Range"),
                            dcc.RangeSlider(
                                id="year-filter",
                                min=min_year,
                                max=max_year,
                                step=1,
                                value=[min_year, max_year],
                                marks=year_marks,
                                tooltip={"placement": "bottom", "always_visible": False},
                            ),
                        ]),
                        html.Div(style={"gridColumn": "span 4"}, children=[
                            html.Label("Price Range"),
                            dcc.RangeSlider(
                                id="price-filter",
                                min=min_price,
                                max=max_price,
                                step=500,
                                value=[min_price, max_price],
                                marks={
                                    min_price: f"${min_price:,}",
                                    max_price: f"${max_price:,}",
                                },
                                tooltip={"placement": "bottom", "always_visible": False},
                            ),
                        ]),
                    ],
                ),

                html.Div(
                    id="kpi-cards",
                    style={
                        "display": "grid",
                        "gridTemplateColumns": "repeat(4, 1fr)",
                        "gap": "14px",
                        "marginBottom": "18px",
                    },
                ),

                html.Div(
                    style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "18px"},
                    children=[
                        dcc.Graph(id="price-by-make"),
                        dcc.Graph(id="country-listings"),
                        dcc.Graph(id="mileage-price-scatter"),
                        dcc.Graph(id="avg-price-year"),
                        dcc.Graph(id="fuel-distribution"),
                        dcc.Graph(id="avg-price-country"),
                    ],
                ),

                html.Div(
                    style={"marginTop": "18px"},
                    children=[dcc.Graph(id="top-models")],
                ),
            ],
        )
    ],
)


def filter_data(
    selected_makes,
    selected_countries,
    selected_fuels,
    selected_sellers,
    selected_conditions,
    year_range,
    price_range,
):
    data = df.copy()

    if selected_makes:
        data = data[data["make"].isin(selected_makes)]

    if selected_countries:
        data = data[data["country"].isin(selected_countries)]

    if selected_fuels:
        data = data[data["fuel_type"].isin(selected_fuels)]

    if selected_sellers:
        data = data[data["seller_type"].isin(selected_sellers)]

    if selected_conditions:
        data = data[data["condition"].isin(selected_conditions)]

    data = data[(data["year"] >= year_range[0]) & (data["year"] <= year_range[1])]
    data = data[(data["price"] >= price_range[0]) & (data["price"] <= price_range[1])]

    return data


@app.callback(
    Output("kpi-cards", "children"),
    Output("price-by-make", "figure"),
    Output("country-listings", "figure"),
    Output("mileage-price-scatter", "figure"),
    Output("avg-price-year", "figure"),
    Output("fuel-distribution", "figure"),
    Output("avg-price-country", "figure"),
    Output("top-models", "figure"),
    Input("make-filter", "value"),
    Input("country-filter", "value"),
    Input("fuel-filter", "value"),
    Input("seller-filter", "value"),
    Input("condition-filter", "value"),
    Input("year-filter", "value"),
    Input("price-filter", "value"),
)
def update_dashboard(
    selected_makes,
    selected_countries,
    selected_fuels,
    selected_sellers,
    selected_conditions,
    year_range,
    price_range,
):
    data = filter_data(
        selected_makes,
        selected_countries,
        selected_fuels,
        selected_sellers,
        selected_conditions,
        year_range,
        price_range,
    )

    if data.empty:
        empty_fig = px.scatter(title="No data available for selected filters")
        empty_fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        cards = [
            html.Div(
                "No listings match the selected filters.",
                style={**CARD_STYLE, "gridColumn": "span 4"},
            )
        ]
        return cards, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig

    kpis = [
        ("Total Listings", f"{len(data):,}"),
        ("Average Price", f"${data['price'].mean():,.0f}"),
        ("Median Mileage", f"{data['mileage'].median():,.0f} mi"),
        ("Countries", f"{data['country'].nunique():,}"),
    ]

    cards = [
        html.Div(
            style=CARD_STYLE,
            children=[
                html.Div(label, style={"color": "#666", "fontSize": "14px"}),
                html.Div(value, style={"fontWeight": "bold", "fontSize": "26px", "marginTop": "6px"}),
            ],
        )
        for label, value in kpis
    ]

    make_summary = (
        data.groupby("make", as_index=False)
        .agg(avg_price=("price", "mean"), listings=("listing_id", "count"))
        .sort_values("avg_price", ascending=False)
        .head(15)
    )

    fig_make = px.bar(
        make_summary,
        x="make",
        y="avg_price",
        text="avg_price",
        hover_data=["listings"],
        title="Average Price by Make",
        labels={"make": "Make", "avg_price": "Average Price ($)", "listings": "Listings"},
    )
    fig_make.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
    fig_make.update_layout(yaxis_tickprefix="$", plot_bgcolor="white", paper_bgcolor="white")

    country_summary = (
        data.groupby("country", as_index=False)
        .agg(
            listings=("listing_id", "count"),
            avg_price=("price", "mean"),
            avg_mileage=("mileage", "mean"),
        )
        .sort_values("listings", ascending=False)
        .head(15)
    )

    fig_country = px.bar(
        country_summary,
        x="country",
        y="listings",
        color="avg_price",
        hover_data={"avg_price": ":,.0f", "avg_mileage": ":,.0f"},
        title="Listings by Country",
        labels={
            "country": "Country",
            "listings": "Number of Listings",
            "avg_price": "Average Price ($)",
            "avg_mileage": "Average Mileage",
        },
    )
    fig_country.update_layout(plot_bgcolor="white", paper_bgcolor="white")

    fig_scatter = px.scatter(
        data,
        x="mileage",
        y="price",
        color="country",
        hover_data=["make", "model", "year", "condition", "seller_type", "fuel_type"],
        title="Mileage vs. Price by Country",
        labels={"mileage": "Mileage", "price": "Price ($)", "country": "Country"},
    )
    fig_scatter.update_layout(yaxis_tickprefix="$", plot_bgcolor="white", paper_bgcolor="white")

    year_summary = (
        data.groupby("year", as_index=False)
        .agg(avg_price=("price", "mean"), listings=("listing_id", "count"))
        .sort_values("year")
    )

    fig_year = px.line(
        year_summary,
        x="year",
        y="avg_price",
        markers=True,
        hover_data=["listings"],
        title="Average Price by Vehicle Year",
        labels={"year": "Year", "avg_price": "Average Price ($)", "listings": "Listings"},
    )
    fig_year.update_layout(yaxis_tickprefix="$", plot_bgcolor="white", paper_bgcolor="white")

    fuel_counts = data["fuel_type"].value_counts().reset_index()
    fuel_counts.columns = ["fuel_type", "count"]

    fig_fuel = px.pie(
        fuel_counts,
        names="fuel_type",
        values="count",
        title="Fuel Type Distribution",
        hole=0.35,
    )
    fig_fuel.update_layout(paper_bgcolor="white")

    avg_country_summary = (
        data.groupby("country", as_index=False)
        .agg(avg_price=("price", "mean"), listings=("listing_id", "count"))
        .sort_values("avg_price", ascending=False)
        .head(15)
    )

    fig_avg_country = px.bar(
        avg_country_summary,
        x="country",
        y="avg_price",
        text="avg_price",
        hover_data=["listings"],
        title="Average Price by Country",
        labels={"country": "Country", "avg_price": "Average Price ($)", "listings": "Listings"},
    )
    fig_avg_country.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
    fig_avg_country.update_layout(yaxis_tickprefix="$", plot_bgcolor="white", paper_bgcolor="white")

    model_summary = (
        data.groupby("make_model", as_index=False)
        .agg(
            avg_price=("price", "mean"),
            avg_mileage=("mileage", "mean"),
            listings=("listing_id", "count"),
        )
        .sort_values("listings", ascending=False)
        .head(20)
    )

    fig_models = px.bar(
        model_summary,
        x="make_model",
        y="listings",
        color="avg_price",
        hover_data={"avg_price": ":,.0f", "avg_mileage": ":,.0f"},
        title="Top Make/Model Combinations by Number of Listings",
        labels={
            "make_model": "Make / Model",
            "listings": "Listings",
            "avg_price": "Average Price ($)",
            "avg_mileage": "Average Mileage",
        },
    )
    fig_models.update_layout(plot_bgcolor="white", paper_bgcolor="white", xaxis_tickangle=-35)

    return (
        cards,
        fig_make,
        fig_country,
        fig_scatter,
        fig_year,
        fig_fuel,
        fig_avg_country,
        fig_models,
    )


if __name__ == "__main__":
    app.run(debug=True)