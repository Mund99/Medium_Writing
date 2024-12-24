import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import math
from plotly.subplots import make_subplots
import pandas as pd
import io


def initialize_session_state():
    """Initialize all session state variables"""
    if "show_chart" not in st.session_state:
        st.session_state.show_chart = False
    if "df" not in st.session_state:
        st.session_state.df = None


def load_data(stock_ticker, start_date, end_date, multi_level_bool):
    """Load data from Yahoo Finance"""
    data = yf.download(
        stock_ticker, start=start_date, end=end_date, multi_level_index=multi_level_bool
    )
    return data


def format_number(number):
    """Format numbers to K (thousands), M (millions), or B (billions)"""
    if number == 0:
        return "0"

    units = ["", "K", "M", "B", "T"]
    k = 1000.0
    magnitude = int(math.floor(math.log(abs(number), k)))
    magnitude = min(magnitude, len(units) - 1)
    val = number / k**magnitude

    if magnitude == 0:
        return f"{val:,.0f}"
    return (
        f"{val:,.1f}{units[magnitude]}"
        if val < 100
        else f"{val:,.0f}{units[magnitude]}"
    )


def create_volume_ticks(y_vals):
    """Create formatted volume axis ticks"""
    tick_vals = []
    tick_texts = []

    max_vol = max(y_vals)
    magnitude = 10 ** math.floor(math.log10(max_vol))
    step = next(s * magnitude for s in [1, 2, 5] if s * magnitude * 4 >= max_vol)

    current = 0
    while current <= max_vol:
        tick_vals.append(current)
        tick_texts.append(format_number(current))
        current += step

    return tick_vals, tick_texts


def plot_stock(df, chart_type="candlestick", symbol="Stock"):
    """Create stock price and volume chart"""
    df.index = pd.to_datetime(df.index).date

    fig = make_subplots(
        rows=2,
        cols=1,
        row_heights=[0.7, 0.3],
        vertical_spacing=0.03,
        shared_xaxes=True,
        specs=[[{"secondary_y": False}], [{"secondary_y": False}]],
    )

    # Add price trace
    if chart_type == "line":
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["Close"],
                name="Price",
                line=dict(color="rgb(0, 90, 170)", width=2),
            ),
            row=1,
            col=1,
        )
    else:
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                name="Price",
                increasing_line_color="rgb(0, 150, 50)",
                decreasing_line_color="rgb(220, 50, 50)",
                increasing_fillcolor="rgba(0, 150, 50, 0.8)",
                decreasing_fillcolor="rgba(220, 50, 50, 0.8)",
                xaxis="x",
            ),
            row=1,
            col=1,
        )

    # Add volume trace
    colors = [
        (
            "rgba(220, 50, 50, 0.5)"
            if row["Close"] < row["Open"]
            else "rgba(0, 150, 50, 0.5)"
        )
        for _, row in df.iterrows()
    ]

    fig.add_trace(
        go.Bar(
            x=df.index,
            y=df["Volume"],
            name="Volume",
            marker=dict(color=colors),
            showlegend=False,
            hoverinfo="skip",
        ),
        row=2,
        col=1,
    )

    # Update layout
    fig.update_layout(
        title=dict(text=f"{symbol} Price Chart", x=0.5, y=0.95, font=dict(size=18)),
        template="plotly_white",
        hovermode="x unified",
        height=700,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=50, r=50, t=50, b=20),
        xaxis_rangeslider_visible=False,
        bargap=0,
        bargroupgap=0,
    )

    # Update price axis
    fig.update_yaxes(
        title_text="Price",
        row=1,
        col=1,
        tickprefix="$",
        tickformat=".2f",
        gridcolor="rgba(128, 128, 128, 0.1)",
        gridwidth=1,
        showgrid=True,
    )

    # Update volume axis
    tick_vals, tick_texts = create_volume_ticks(df["Volume"].values)
    fig.update_yaxes(
        title_text="Volume",
        row=2,
        col=1,
        gridcolor="rgba(128, 128, 128, 0.1)",
        gridwidth=1,
        showgrid=True,
        tickmode="array",
        tickvals=tick_vals,
        ticktext=tick_texts,
    )

    # Update x-axes
    for row in [1, 2]:
        fig.update_xaxes(
            row=row,
            col=1,
            type="category",
            tickangle=0,
            tickfont=dict(size=10),
            gridcolor="rgba(128, 128, 128, 0.1)",
            gridwidth=1,
            showgrid=True,
            nticks=8,
            rangeslider_visible=False,
        )

    return fig


def setup_page():
    """Configure page settings and display header"""
    st.set_page_config(
        page_title="Stock Price Visualizer", page_icon="📈", layout="wide"
    )
    st.title("📈 Stock Price Visualizer")
    st.markdown(
        "This app provides visualization of historical stock prices. Enter a stock ticker and select your preferred date range!"
    )


def get_date_range(selected_range):
    """Get start and end dates based on selected range"""
    end_date = datetime.now()

    if selected_range == "Custom":
        end_date = st.date_input("End Date", value=end_date)
        start_date = st.date_input(
            "Start Date", value=end_date - timedelta(days=365), max_value=end_date
        )
        if start_date >= end_date:
            st.error("Start date must be before end date")
    else:
        date_ranges = {"1 Month": 30, "3 Months": 90, "6 Months": 180, "1 Year": 365}
        start_date = end_date - timedelta(days=date_ranges[selected_range])

    return start_date, end_date


def show_stock_metrics(df, info):
    """Display stock metrics in columns"""
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Current Price",
            f"${df['Close'].iloc[-1]:.2f}",
            f"{((df['Close'].iloc[-1] - df['Close'].iloc[-2])/df['Close'].iloc[-2]*100):.2f}%",
        )

    with col2:
        if "marketCap" in info:
            st.metric("Market Cap", format_number(info["marketCap"]))

    with col3:
        if "volume" in info:
            st.metric("Volume", format_number(info["volume"]))


def main():
    initialize_session_state()
    setup_page()

    # Sidebar configuration
    with st.sidebar:
        st.header("📊 Configuration")
        stock_ticker = st.text_input("Enter Stock Ticker:", "AAPL").upper().strip()
        selected_range = st.selectbox(
            "Select Time Period:",
            ["1 Month", "3 Months", "6 Months", "1 Year", "Custom"],
        )
        start_date, end_date = get_date_range(selected_range)

        if st.button("Show Chart"):
            st.session_state.show_chart = True

    # Main content
    if st.session_state.show_chart:
        try:
            with st.spinner(f"Fetching data for {stock_ticker}..."):
                st.session_state.df = load_data(
                    stock_ticker, start_date, end_date, multi_level_bool=False
                )

                if st.session_state.df.empty:
                    st.error(
                        f"No data found for ticker {stock_ticker}. Please check the symbol and try again."
                    )
                    return

                stock = yf.Ticker(stock_ticker)
                show_stock_metrics(st.session_state.df, stock.info)

                chart_type = st.radio("Select Chart Type:", ["Candlestick", "Line"])

                with st.spinner("Generating chart..."):
                    fig = plot_stock(
                        st.session_state.df, chart_type.lower(), stock_ticker
                    )
                    st.plotly_chart(fig, use_container_width=True)

                with st.expander("Show Raw Data"):
                    st.dataframe(st.session_state.df)

                # Prepare Excel download
                buffer = io.BytesIO()
                df_excel = st.session_state.df.copy()
                df_excel.index = pd.to_datetime(df_excel.index).tz_localize(None)

                with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                    df_excel.to_excel(writer, sheet_name="Stock Data")

                st.download_button(
                    label="Download Data as Excel",
                    data=buffer,
                    file_name=f'{stock_ticker}_stock_data_{start_date.strftime("%Y%m%d")}_{end_date.strftime("%Y%m%d")}.xlsx',
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
