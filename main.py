import sys
import os
from flask import Flask, render_template, request, redirect, url_for
from lsf import LSF
import yaml
import plotly.express as px

app = Flask(__name__)

with open('config.yaml', 'r') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

categories = config['transaction-category']

csv_path = sys.argv[1] if len(sys.argv) > 1 else 'statement.csv'
statement = LSF(csv_path)
transactions = statement.get_transactions()

# Keyed by transaction index (int), value is {amount: str, category: str}
_state: dict[int, dict] = {}


@app.route('/')
def index():
    return redirect(url_for('transaction', idx=0))


@app.route('/transaction/<int:idx>', methods=['GET', 'POST'])
def transaction(idx):
    if not transactions:
        return redirect(url_for('chart'))

    if request.method == 'POST':
        action = request.form.get('action', 'next')
        _state[idx] = {
            'amount': request.form.get('amount', transactions[idx].amount),
            'category': request.form.get('category', ''),
        }
        if action == 'back':
            return redirect(url_for('transaction', idx=max(0, idx - 1)))
        if action == 'finish':
            return redirect(url_for('chart'))
        next_idx = idx + 1
        if next_idx >= len(transactions):
            return redirect(url_for('chart'))
        return redirect(url_for('transaction', idx=next_idx))

    saved = _state.get(idx, {})
    return render_template(
        'transaction.html',
        t=transactions[idx],
        idx=idx,
        total=len(transactions),
        amount=saved.get('amount', transactions[idx].amount),
        selected_category=saved.get('category', ''),
        categories=categories,
    )


@app.route('/chart')
def chart():
    totals: dict[str, float] = {cat: 0.0 for cat in categories}
    for data in _state.values():
        cat = data.get('category', '')
        if cat and cat in totals:
            try:
                totals[cat] += float(data.get('amount', 0))
            except (ValueError, TypeError):
                pass

    filtered = {k: v for k, v in totals.items() if v > 0}
    if filtered:
        fig = px.pie(
            values=list(filtered.values()),
            names=list(filtered.keys()),
            title='Expenses by Category',
        )
    else:
        fig = px.pie(values=[1], names=['No categorized expenses'], title='Expenses by Category')

    chart_html = fig.to_html(include_plotlyjs=True, full_html=False)
    return render_template('chart.html', chart_html=chart_html)


if __name__ == '__main__':
    app.run(debug=True)
