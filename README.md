
# Trading Strategies Backtest: Stochastic Oscillator & Bollinger Bands

## Introduction

This repository contains backtesting results for two distinct trading strategies as shared per Rayner Teo, as shared on his YouTube channel. The strategies leverage the Stochastic Oscillator and Bollinger Bands to identify potential buy signals in bullish market trends. This document outlines the methodology, entry and exit rules, and acknowledgments for both strategies. The backtests were conducted on EOG stock data spanning a period of 15 years.

## Strategies Overview

## 1. Stochastic Trading System

#### Entry Conditions

- The asset is trading above its 200-day moving average, indicating a bullish trend.
- The 10-period stochastic %K is below 5, suggesting oversold conditions.

#### Entry Rules

- Place a 3% buy limit order below the previous day's closing price.

#### Exit Rules

- Exit on a higher closing price.
- Or, exit after 10 trading days, regardless of the price movement.

### Backtesting Results
- Times in market: 18
- Starting Portfolio Value: $12,000.00
- Final Portfolio Value: $14,436.16
- Gross Return: $2,436.16


## 2. Bollinger Band System

#### Entry Conditions

- The stock is trading above its 200-day moving average, signaling a bullish trend.
- The stock closes 2.5 standard deviations below the 20-day Bollinger Band, indicating an oversold condition.

#### Entry Rules

- Place a 3% buy limit order below the previous day's closing price.

#### Exit Rules

- Exit when the 2-day RSI crosses above 50, suggesting a potential reversal from oversold conditions.
- Alternatively, exit after 10 trading days, irrespective of price action.

### Backtesting Results
- Times in market: 12
- Starting Portfolio Value: $12,000.00
- Final Portfolio Value: $16,041.78
- Gross Return: $4,041.78

The above results demonstrate the performance of each system over the backtesting period with a starting portfolio value of $12,000. The Bollinger Band system showed a higggesting a more profher gross return, suitable strategy over the 15 years of EOG data tested. These results are specific to the historical data and are not indicative of future performance.

## Acknowledgments
 The Stochastic Trading System is inspired by [this video on Stochastic trading](https://www.youtube.com/watch?v=viLst9ZAC6Y&t), and the Bollinger Band System by [this video on Bollinger Bands](https://www.youtube.com/watch?v=CxFv_EUY0ZA&t).