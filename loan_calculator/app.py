from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from loan_calculator import calculate_loan_metrics

app = Dash(__name__)

# External CSS stylesheets for additional styling
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# Define a vibrant color scheme
colors = {
    'background': '#f4f4f4',
    'text': '#1a1a1a',
    'accent': '#ff4500'  # Choose a vibrant color for accents
}

def create_layout():
    return html.Div(style={'backgroundColor': colors['background'], 'padding': '20px'}, children=[
        html.H1("Loan Calculator", style={'textAlign': 'center', 'color': colors['text']}),

        html.Div([
            html.Div([
                html.Label("Total Loan Amount:", style={'color': colors['text']}),
                dcc.Input(id="total_loan", type="number", placeholder="Enter total loan amount", required=True,
                          style={'margin-bottom': '20px', 'color': colors['text']}),
            ], style={'margin-bottom': '20px', 'textAlign': 'center'}),

            html.Div([
                html.Label("Loan Tenure (years):", style={'color': colors['text']}),
                dcc.Input(id="tenure", type="number", placeholder="Enter loan tenure in years", required=True,
                          style={'margin-bottom': '20px', 'color': colors['text']}),
            ], style={'margin-bottom': '20px', 'textAlign': 'center'}),

            html.Div([
                html.Label("Interest Rate p.a. (%):", style={'color': colors['text']}),
                dcc.Input(id="interest_rate", type="number", placeholder="Enter annual interest rate", required=True,
                          style={'margin-bottom': '20px', 'color': colors['text']}),
            ], style={'margin-bottom': '20px', 'textAlign': 'center'}),

            html.Button("Calculate", id="calculate_button", n_clicks=0, style={'margin-top': '20px', 'background-color': colors['accent'], 'color': colors['background']}),
        ], style={'textAlign': 'center'}),

        html.Div(id="result", style={'margin-top': '30px', 'textAlign': 'center', 'color': colors['text'], 'fontSize': '18px'})
    ])

app.layout = create_layout()

@app.callback(
    Output("result", "children"),
    Input("calculate_button", "n_clicks"),
    [Input("total_loan", "value"), Input("tenure", "value"), Input("interest_rate", "value")]
)
def update_result(n_clicks, total_loan, tenure, interest_rate):
    if n_clicks > 0:
        monthly_installment, total_repayment, effective_interest_rate = calculate_loan_metrics(total_loan, tenure, interest_rate)

        # Calculate additional financial details
        total_interest = total_repayment - total_loan
        tenure_yr = int(tenure)
        tenure_mth = int(tenure_yr * 12)
        yearly_interest = total_interest / tenure_yr
        monthly_interest = total_interest / (tenure_yr * 12)

        # Format dollar amounts with commas
        formatted_monthly_installment = "${:,.2f}".format(monthly_installment)
        formatted_total_repayment = "${:,.2f}".format(total_repayment)
        formatted_total_loan = "${:,.2f}".format(total_loan)
        formatted_total_interest = "${:,.2f}".format(total_interest)
        formatted_yearly_interest = "${:,.2f}".format(yearly_interest)
        formatted_monthly_interest = "${:,.2f}".format(monthly_interest)

        result_html = html.Div([
            html.H3("Loan Details", style={'color': colors['accent']}),
            html.P(f"Principal Amount: {formatted_total_loan}"),
            html.P(f"Interest Rate: {interest_rate}%"),
            html.P(f"Loan Tenure: {tenure_yr} years ({tenure_mth} months)"),

            html.H3("Financial Summary", style={'color': colors['accent']}),
            html.P(f"Total Repayment: {formatted_total_repayment}"),
            html.P(f"Total Interest: {formatted_total_interest}"),
            html.P(f"Yearly Interest: {formatted_yearly_interest}"),
            html.P(f"Monthly Interest: {formatted_monthly_interest}"),
            html.P(f"Monthly Installment: {formatted_monthly_installment}"),
            html.P(f"Effective Interest Rate (EIR): {(effective_interest_rate*100):,.2f}%")
        ], style={'margin-top': '20px', 'textAlign': 'center'})

        return result_html



if __name__ == "__main__":
    app.run_server(debug=False)


