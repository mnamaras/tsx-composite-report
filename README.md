# tsx-composite-report

A two-step process that pulls daily price/volume data for every TSX Composite constituent, and then generates an HTML "morning report" with sector performance, top movers, unusual volume flags, and charts

1. input.py
Pulls data from yfinance for the full TSX composite list, and gets sectors, market caps, close, return %, volume, 20 day average volume, and volume ratio into a CSV
   
2. output.py
Reads data from input.py and outputs sector-level average returns, gainers/losers, volume flags, and a headline statement, alongside charts, into an HTML report

Requirements:
1. Python
2. yfinance, pandas, numpy, matplotlib

Next steps:
1. Validation: check that the report generated matches the current day to avoid using stale data, and print a flag in case this isn't what was wanted
2. TSX Composite list: membership changes over time, so the list should be sourced or refreshed periodically automatically
3. Prettier report styling
4. Commentary: the headline statement just fills a hardcoded template, see if maybe Claude API call can be used to generate a more accurate paragraph
