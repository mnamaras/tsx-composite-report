import numpy as np
import pandas as pd
import datetime as dt
import yfinance as yf

tsx_composite_tickers = [
    'AAUC.TO', 'AAV.TO', 'ABRA.TO', 'ABX.TO', 'AC.TO', 'ACO-X.TO', 'AEM.TO', 'AG.TO',
    'AGI.TO', 'AIF.TO', 'ALA.TO', 'ALS.TO', 'AP-UN.TO', 'AQN.TO', 'ARE.TO', 'ARIS.TO',
    'ARX.TO', 'ASM.TO', 'ATD.TO', 'ATH.TO', 'ATRL.TO', 'ATS.TO', 'ATZ.TO', 'AYA.TO',
    'BAM.TO', 'BB.TO', 'BBD-B.TO', 'BBUC.TO', 'BCE.TO', 'BDGI.TO', 'BDT.TO', 'BEI-UN.TO',
    'BEP-UN.TO', 'BHC.TO', 'BIP-UN.TO', 'BIR.TO', 'BLX.TO', 'BMO.TO', 'BN.TO', 'BNS.TO',
    'BTE.TO', 'BTO.TO', 'BYD.TO', 'CAE.TO', 'CAR-UN.TO', 'CCA.TO', 'CCL-B.TO', 'CCO.TO',
    'CEU.TO', 'CG.TO', 'CHP-UN.TO', 'CIGI.TO', 'CJT.TO', 'CLS.TO', 'CM.TO', 'CNQ.TO',
    'CNR.TO', 'CP.TO', 'CPX.TO', 'CRR-UN.TO', 'CRT-UN.TO', 'CS.TO', 'CSH-UN.TO', 'CSU.TO',
    'CTC-A.TO', 'CU.TO', 'CURA.TO', 'CVE.TO', 'DFY.TO', 'DIR-UN.TO', 'DML.TO', 'DOL.TO',
    'DOO.TO', 'DPM.TO', 'DSG.TO', 'DSV.TO', 'EDR.TO', 'EFN.TO', 'EFR.TO', 'EFX.TO',
    'EIF.TO', 'ELD.TO', 'EMA.TO', 'EMP-A.TO', 'ENB.TO', 'EQB.TO', 'EQX.TO', 'ERO.TO',
    'EXE.TO', 'FCR-UN.TO', 'FFH.TO', 'FM.TO', 'FNV.TO', 'FRU.TO', 'FSV.TO', 'FTS.TO',
    'FTT.TO', 'FVI.TO', 'GEI.TO', 'GFL.TO', 'GIB-A.TO', 'GIL.TO', 'GMIN.TO', 'GRT-UN.TO',
    'GWO.TO', 'H.TO', 'HBM.TO', 'HPS-A.TO', 'HR-UN.TO', 'HWX.TO', 'IAG.TO', 'IAU.TO',
    'IFC.TO', 'IGM.TO', 'IMG.TO', 'IMO.TO', 'IPCO.TO', 'IVN.TO', 'JWEL.TO', 'K.TO',
    'KEL.TO', 'KEY.TO', 'KMP-UN.TO', 'KNT.TO', 'KXS.TO', 'L.TO', 'LAC.TO', 'LB.TO',
    'LIF.TO', 'LNR.TO', 'LSPD.TO', 'LUG.TO', 'LUN.TO', 'MAU.TO', 'MDA.TO', 'MFC.TO',
    'MFI.TO', 'MG.TO', 'MRU.TO', 'MTL.TO', 'MX.TO', 'NA.TO', 'NFI.TO', 'NG.TO',
    'NGEX.TO', 'NPI.TO', 'NTR.TO', 'NWC.TO', 'NXE.TO', 'OGC.TO', 'OLA.TO', 'ONEX.TO',
    'OR.TO', 'OTEX.TO', 'PAAS.TO', 'PBH.TO', 'PEY.TO', 'PMZ-UN.TO', 'POU.TO', 'POW.TO',
    'PPL.TO', 'PPTA.TO', 'PSK.TO', 'PXT.TO', 'QBR-B.TO', 'QSR.TO', 'RBA.TO', 'RCH.TO',
    'RCI-B.TO', 'REI-UN.TO', 'RUS.TO', 'RY.TO', 'SAP.TO', 'SCR.TO', 'SDE.TO', 'SEA.TO',
    'SES.TO', 'SHOP.TO', 'SIA.TO', 'SII.TO', 'SJ.TO', 'SKE.TO', 'SLF.TO', 'SOBO.TO',
    'SPB.TO', 'SRU-UN.TO', 'SSRM.TO', 'STN.TO', 'SU.TO', 'SVM.TO', 'SXGC.TO', 'T.TO',
    'TA.TO', 'TD.TO', 'TECK-B.TO', 'TFII.TO', 'TFPM.TO', 'TIH.TO', 'TKO.TO', 'TOU.TO',
    'TPZ.TO', 'TRI.TO', 'TRP.TO', 'TSU.TO', 'TVE.TO', 'TVK.TO', 'TXG.TO', 'USA.TO',
    'VET.TO', 'VNP.TO', 'VZLA.TO', 'WCN.TO', 'WCP.TO', 'WDO.TO', 'WFG.TO', 'WN.TO',
    'WPM.TO', 'WSP.TO', 'X.TO',
]

# getting sector info and market cap
records = []
for i, ticker in enumerate(tsx_composite_tickers):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        records.append({
            'ticker': ticker,
            'sector': info.get('sector'),
            'market_cap': info.get('marketCap')
        })
    except Exception as e:
        print(f"Failed on {ticker}: {e}")
        records.append({'ticker': ticker, 'sector': None, 'market_cap': None})

df = pd.DataFrame(records)
df.to_csv('sector_lookup.csv', index=False)
print("Sectors and Market Caps extracted to sector_lookup.csv")


# getting current 25 day data
data = yf.download(tsx_composite_tickers, period='25d', group_by='ticker', auto_adjust=True)

summary_records = []
history_records = []

for ticker in tsx_composite_tickers:
    try:
        hist = data[ticker].dropna()
        if len(hist) < 2:
            continue

        close_today = hist['Close'].iloc[-1]
        close_yesterday = hist['Close'].iloc[-2]
        volume_today = hist['Volume'].iloc[-1]
        avg_volume_20d = hist['Volume'].iloc[:-1].tail(20).mean()  # 20 days excluding today

        summary_records.append({
            'ticker': ticker,
            'date': hist.index[-1].strftime('%Y-%m-%d'),
            'close_today': close_today,
            'close_yesterday': close_yesterday,
            'return_pct': (close_today - close_yesterday) / close_yesterday,
            'volume_today': volume_today,
            'avg_volume_20d': avg_volume_20d,
            'volume_ratio': volume_today / avg_volume_20d if avg_volume_20d else None
        })

        for date, row in hist.iterrows():
            history_records.append({
                'ticker': ticker,
                'date': date.strftime('%Y-%m-%d'),
                'close': row['Close'],
                'volume': row['Volume']
            })

    except Exception as e:
        print(f"Skipping {ticker}: {e}")

pd.DataFrame(summary_records).to_csv("daily_data.csv", index=False)
print("Saved to daily_data.csv")

pd.DataFrame(history_records).to_csv("daily_history.csv", index=False)
print("Saved to daily_history.csv")