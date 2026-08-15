import pandas as pd
import datetime as dt
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import base64

today_str = dt.date.today().strftime('%Y-%m-%d')

daily = pd.read_csv('daily_data.csv')
sectors = pd.read_csv('sector_lookup.csv')
history = pd.read_csv('daily_history.csv', parse_dates=['date'])  # NEW

merged = daily.merge(sectors, on='ticker', how='left')
merged = merged.dropna(subset=['sector'])

# sector returns
sector_returns = merged.groupby('sector')['return_pct'].mean().sort_values(ascending=False)

# top gainers/losers
top_gainers = merged.nlargest(5, 'return_pct')[['ticker', 'return_pct']]
top_losers = merged.nsmallest(5, 'return_pct')[['ticker', 'return_pct']]

# volume flags
volume_flags_high = merged[merged['volume_ratio'] > 2].sort_values('volume_ratio', ascending=False).head(5)
volume_flags_low = merged[merged['volume_ratio'] < 0.5].sort_values('volume_ratio', ascending=True).head(5)

# ---------- headline index move ----------
index_df = yf.download('^GSPTSE', period='25d', auto_adjust=True)  # 25d so we have chart history too
index_close_today = float(index_df['Close'].iloc[-1])
index_close_yesterday = float(index_df['Close'].iloc[-2])
index_return_pct = (index_close_today - index_close_yesterday) / index_close_yesterday

headline = f"TSX Composite closed at {index_close_today:,.2f}, {index_return_pct*100:+.2f}% on the day"

# ---------- auto-generated commentary sentence ----------
top_sector = sector_returns.index[0]
top_sector_return = sector_returns.iloc[0]

sector_subset = merged[merged['sector'] == top_sector]
sector_gainers = sector_subset[sector_subset['return_pct'] > 0]

if not sector_gainers.empty:
    top_mover = sector_gainers.loc[sector_gainers['volume_ratio'].idxmax()]
    commentary = (
        f"{top_sector} led gains today, up {top_sector_return*100:.1f}%, "
        f"driven by {top_mover['ticker']}'s volume spike of {top_mover['volume_ratio']:.1f}x average"
    )
else:
    commentary = f"{top_sector} led gains today, up {top_sector_return*100:.1f}%"

print(headline)
print(commentary)
print("\nSECTOR RETURNS\n", sector_returns)
print("\nTOP GAINERS\n", top_gainers)
print("\nTOP LOSERS\n", top_losers)
print("\nHIGH VOLUME FLAGS\n", volume_flags_high[['ticker', 'sector', 'volume_ratio']])
print("\nLOW VOLUME FLAGS\n", volume_flags_low[['ticker', 'sector', 'volume_ratio']])


# ---------- CHARTS ----------

def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=120)
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return encoded

def normalize_series(ticker):
    """% change from day 1, indexed by date."""
    g = history[history['ticker'] == ticker].sort_values('date')
    day1_close = g['close'].iloc[0]
    normalized = (g['close'] / day1_close - 1) * 100
    normalized.index = g['date']
    return normalized

def make_line_chart(series_dict, title, ylabel):
    fig, ax = plt.subplots(figsize=(6, 4))
    for label, series in series_dict.items():
        ax.plot(series.index, series.values, label=label, linewidth=1.8)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.axhline(0, color='gray', linewidth=0.8, linestyle='--')
    ax.legend(fontsize=8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    fig.autofmt_xdate()
    return fig_to_base64(fig)

def make_volume_chart(tickers, title):
    fig, ax = plt.subplots(figsize=(6, 4))
    for t in tickers:
        g = history[history['ticker'] == t].sort_values('date')
        ax.plot(g['date'], g['volume'], label=t, linewidth=1.8)
    ax.set_title(title)
    ax.set_ylabel('Volume')
    ax.legend(fontsize=8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    fig.autofmt_xdate()
    return fig_to_base64(fig)

# index chart
index_series = (index_df['Close'] / index_df['Close'].iloc[0] - 1) * 100
index_series = index_series.squeeze()
index_chart_b64 = make_line_chart({'TSX Composite': index_series}, 'Index Performance (20d, normalized)', '% change')

# gainers/losers charts
gainer_series = {t: normalize_series(t) for t in top_gainers['ticker']}
gainers_chart_b64 = make_line_chart(gainer_series, 'Top Gainers (normalized)', '% change')

loser_series = {t: normalize_series(t) for t in top_losers['ticker']}
losers_chart_b64 = make_line_chart(loser_series, 'Top Losers (normalized)', '% change')

# volume charts
vol_high_chart_b64 = make_volume_chart(volume_flags_high['ticker'], 'Unusual Volume — High')
vol_low_chart_b64 = make_volume_chart(volume_flags_low['ticker'], 'Unusual Volume — Low')

print("\nAll charts generated.")

# ---------- HTML REPORT ----------

def df_to_html_rows(df, cols, pct_cols=None):
    """Turn a dataframe into simple HTML table rows."""
    pct_cols = pct_cols or []
    rows = ""
    for _, row in df.iterrows():
        cells = ""
        for c in cols:
            val = row[c]
            if c in pct_cols:
                val = f"{val*100:+.2f}%"
            elif isinstance(val, float):
                val = f"{val:.2f}"
            cells += f"<td>{val}</td>"
        rows += f"<tr>{cells}</tr>"
    return rows

gainers_rows = df_to_html_rows(top_gainers, ['ticker', 'return_pct'], pct_cols=['return_pct'])
losers_rows = df_to_html_rows(top_losers, ['ticker', 'return_pct'], pct_cols=['return_pct'])
vol_high_rows = df_to_html_rows(volume_flags_high, ['ticker', 'sector', 'volume_ratio'])
vol_low_rows = df_to_html_rows(volume_flags_low, ['ticker', 'sector', 'volume_ratio'])

report_date = dt.date.today().strftime('%B %d, %Y')

html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    body {{
        font-family: -apple-system, Arial, sans-serif;
        max-width: 950px;
        margin: 20px auto;
        color: #222;
    }}
    .box {{
        border: 1px solid #ccc;
        border-radius: 4px;
        padding: 16px;
        margin-bottom: 12px;
    }}
    .row {{
        display: flex;
        gap: 12px;
    }}
    .row .box {{
        flex: 1;
    }}
    h1 {{ font-size: 20px; margin: 0 0 4px 0; }}
    h2 {{ font-size: 14px; margin: 0 0 8px 0; color: #555; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    td {{ padding: 4px 6px; border-bottom: 1px solid #eee; }}
    img {{ width: 100%; height: auto; }}
    .commentary {{ font-size: 14px; line-height: 1.5; }}
</style>
</head>
<body>

<div class="box">
    <h1>TSX Composite Daily Report - {report_date}</h1>
    <p style="font-size:15px; margin:6px 0 0 0;"><strong>{headline}</strong></p>
</div>

<div class="row">
    <div class="box">
        <h2>Commentary</h2>
        <p class="commentary">{commentary}</p>
    </div>
    <div class="box">
        <h2>Index Performance</h2>
        <img src="data:image/png;base64,{index_chart_b64}">
    </div>
</div>

<div class="row">
    <div class="box">
        <h2>Top Gainers</h2>
        <table>{gainers_rows}</table>
        <h2 style="margin-top:16px;">Top Losers</h2>
        <table>{losers_rows}</table>
    </div>
    <div class="box">
        <h2>Gainers (normalized)</h2>
        <img src="data:image/png;base64,{gainers_chart_b64}">
        <h2 style="margin-top:12px;">Losers (normalized)</h2>
        <img src="data:image/png;base64,{losers_chart_b64}">
    </div>
</div>

<div class="row">
    <div class="box">
        <h2>High Volume Flags</h2>
        <table>{vol_high_rows}</table>
        <h2 style="margin-top:16px;">Low Volume Flags</h2>
        <table>{vol_low_rows}</table>
    </div>
    <div class="box">
        <h2>Unusual Volume — High</h2>
        <img src="data:image/png;base64,{vol_high_chart_b64}">
        <h2 style="margin-top:12px;">Unusual Volume — Low</h2>
        <img src="data:image/png;base64,{vol_low_chart_b64}">
    </div>
</div>

</body>
</html>
"""

output_filename = f"tsx_report_{today_str}.html"
with open(output_filename, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\nReport saved to {output_filename}")