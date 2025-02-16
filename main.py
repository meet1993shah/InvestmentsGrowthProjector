from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import platform
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Color palette for the graph
COLOR_PALETTE = [
    'rgb(255, 99, 132)', 'rgb(54, 162, 235)', 'rgb(255, 206, 86)',
    'rgb(75, 192, 192)', 'rgb(153, 102, 255)', 'rgb(255, 159, 64)',
    'rgb(255, 99, 132)', 'rgb(54, 162, 235)', 'rgb(255, 99, 71)',
    'rgb(60, 179, 113)', 'rgb(255, 105, 180)', 'rgb(123, 104, 238)'
]

def create_growth_projection(years: int, initial_amounts: list, savings: list, rates: list):
    """
    Generate the growth projections for the investments over the specified years.
    """
    growth = []
    X = list(range(years + 1))  # Years

    for p, s, r in zip(initial_amounts, savings, rates):
        r = r / 100.0  # Convert percentage to decimal
        temp_growth = [p]
        for _ in range(1, years + 1):
            temp_growth.append(temp_growth[-1] * (1 + r) + s)
        growth.append(temp_growth)

    return X, growth

def extract_investment_data(form_data, count):
    """
    Extract investment details from the submitted form data.
    """
    initial_amounts = [float(form_data[f'initial_amount_{i}']) for i in range(count)]
    rates = [float(form_data[f'rate_{i}']) for i in range(count)]
    savings = [float(form_data[f'savings_{i}']) for i in range(count)]
    
    return initial_amounts, rates, savings

def prepare_chart_data(X, Y_list, initial_amounts, rates, savings):
    """
    Prepare JSON data for Chart.js with detailed labels.
    """
    return {
        'labels': X,
        'datasets': [
            {
                'label': f'Investment {i+1} (p = {initial_amounts[i]}, r = {rates[i]}%, s = {savings[i]})',
                'data': Y,
                'fill': False,
                'borderColor': COLOR_PALETTE[i % len(COLOR_PALETTE)],
                'backgroundColor': COLOR_PALETTE[i % len(COLOR_PALETTE)],
                'tension': 0.1
            }
            for i, Y in enumerate(Y_list)
        ]
    }

@app.route('/')
def index():
    """Render the home page to enter the number of investments."""
    return render_template('index.html')

@app.route('/investment_details', methods=['GET'])
def investment_details_get():
    """Render the investment details form (GET request)."""
    chart_count = request.args.get('chart_count', default=1, type=int)
    return render_template('investment_details.html', chart_count=chart_count)

@app.route('/investment_details', methods=['POST'])
def investment_details_post():
    """Process investment details and redirect to the chart page."""
    try:
        # Extract form data
        chart_count = int(request.form['chart_count'])
        years = int(request.form['years'])

        # Store chart_count in session for back navigation
        session['chart_count'] = chart_count  

        # Extract investment details
        initial_amounts, rates, savings = extract_investment_data(request.form, chart_count)

        # Generate growth projections
        X, Y_list = create_growth_projection(years, initial_amounts, savings, rates)

        # Prepare chart data with detailed labels
        chart_data = prepare_chart_data(X, Y_list, initial_amounts, rates, savings)

        # Store chart data in session storage for retrieval on /chart_display
        session['chart_data'] = chart_data

        # Redirect to the chart display page
        return redirect(url_for('chart_display'))

    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/chart_display', methods=['GET'])
def chart_display():
    """Render the chart display page."""
    return render_template('chart_display.html')

if __name__ == '__main__':
    if platform.system() == 'Android':
        from android.permissions import Permission, request_permissions
        request_permissions([Permission.INTERNET, Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
    app.run(debug=False, port=8080)

