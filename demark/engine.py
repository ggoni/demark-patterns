import pandas as pd
import numpy as np

class DeMarkEngine:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def calculate_setup(self) -> pd.DataFrame:
        """
        Calculate TD Setup (9-count).
        Strict Compliance:
        - Requires a Price Flip to start count.
        - Includes Perfection check (low/high comparison).
        """
        close = self.df['Close']
        low = self.df['Low']
        high = self.df['High']
        
        self.df['buy_setup_count'] = 0
        self.df['sell_setup_count'] = 0
        self.df['buy_perfect'] = False
        self.df['sell_perfect'] = False
        
        b_count = 0
        s_count = 0
        
        for i in range(5, len(self.df)):
            # Buy Setup
            # Condition: close.iloc[i] < close.iloc[i-4]
            # Start (count 1) requires price flip: close.iloc[i-1] >= close.iloc[i-5]
            if close.iloc[i] < close.iloc[i-4]:
                if b_count == 0:
                    if close.iloc[i-1] >= close.iloc[i-5]: # Price Flip
                        b_count = 1
                else:
                    b_count += 1
            else:
                b_count = 0
            
            self.df.at[self.df.index[i], 'buy_setup_count'] = b_count
            
            if b_count == 9:
                # Perfection: min(low.iloc[i], low.iloc[i-1]) <= min(low.iloc[i-2], low.iloc[i-3])
                if min(low.iloc[i], low.iloc[i-1]) <= min(low.iloc[i-2], low.iloc[i-3]):
                    self.df.at[self.df.index[i], 'buy_perfect'] = True

            # Sell Setup
            # Condition: close.iloc[i] > close.iloc[i-4]
            # Start (count 1) requires price flip: close.iloc[i-1] <= close.iloc[i-5]
            if close.iloc[i] > close.iloc[i-4]:
                if s_count == 0:
                    if close.iloc[i-1] <= close.iloc[i-5]: # Price Flip
                        s_count = 1
                else:
                    s_count += 1
            else:
                s_count = 0
            
            self.df.at[self.df.index[i], 'sell_setup_count'] = s_count
            
            if s_count == 9:
                # Perfection: max(high.iloc[i], high.iloc[i-1]) >= max(high.iloc[i-2], high.iloc[i-3])
                if max(high.iloc[i], high.iloc[i-1]) >= max(high.iloc[i-2], high.iloc[i-3]):
                    self.df.at[self.df.index[i], 'sell_perfect'] = True

        return self.df
        
    def validate_intersection(self) -> pd.DataFrame:
        """
        Validate TD Intersection criteria.
        Buy Intersection: High[8 or 9] >= Low[3-7]
        Sell Intersection: Low[8 or 9] <= High[3-7]
        """
        self.df['buy_intersection'] = False
        self.df['sell_intersection'] = False
        
        for i in range(len(self.df)):
            # Buy Setup Intersection
            if self.df.iloc[i]['buy_setup_count'] in [8, 9]:
                setup_start = i - (self.df.iloc[i]['buy_setup_count'] - 1)
                # Need at least 8 bars for a check
                if setup_start >= 0:
                    lows_3_to_7 = self.df.iloc[setup_start+2 : setup_start+7]['Low']
                    if not lows_3_to_7.empty and self.df.iloc[i]['High'] >= lows_3_to_7.min():
                        self.df.at[self.df.index[i], 'buy_intersection'] = True

            # Sell Setup Intersection
            if self.df.iloc[i]['sell_setup_count'] in [8, 9]:
                setup_start = i - (self.df.iloc[i]['sell_setup_count'] - 1)
                if setup_start >= 0:
                    highs_3_to_7 = self.df.iloc[setup_start+2 : setup_start+7]['High']
                    if not highs_3_to_7.empty and self.df.iloc[i]['Low'] <= highs_3_to_7.max():
                        self.df.at[self.df.index[i], 'sell_intersection'] = True
                        
        return self.df
    def calculate_countdown(self) -> pd.DataFrame:
        """
        Calculate TD Countdown (13-count).
        Strict Compliance:
        - Bar 13 Qualification: Close[13] vs Close[8].
        """
        close = self.df['Close']
        high = self.df['High']
        low = self.df['Low']
        
        self.df['buy_countdown_count'] = 0
        self.df['sell_countdown_count'] = 0
        self.df['buy_countdown_recycled'] = False
        self.df['sell_countdown_recycled'] = False

        active_buy_countdown = False
        buy_count = 0
        buy_bar8_close = np.nan
        buy_ext_count = 0

        active_sell_countdown = False
        sell_count = 0
        sell_bar8_close = np.nan
        sell_ext_count = 0

        for i in range(len(self.df)):
            # Recycle tracking: consecutive setup-qualifying bars while countdown is active.
            if active_buy_countdown and i >= 4:
                if close.iloc[i] < close.iloc[i-4]:
                    buy_ext_count += 1
                else:
                    buy_ext_count = 0

                if buy_ext_count > 18:
                    self.df.at[self.df.index[i], 'buy_countdown_recycled'] = True
                    active_buy_countdown = False
                    buy_count = 0
                    buy_bar8_close = np.nan
                    buy_ext_count = 0

            if active_sell_countdown and i >= 4:
                if close.iloc[i] > close.iloc[i-4]:
                    sell_ext_count += 1
                else:
                    sell_ext_count = 0

                if sell_ext_count > 18:
                    self.df.at[self.df.index[i], 'sell_countdown_recycled'] = True
                    active_sell_countdown = False
                    sell_count = 0
                    sell_bar8_close = np.nan
                    sell_ext_count = 0

            # Start/Reset on Setup completion
            if self.df.iloc[i]['buy_setup_count'] == 9:
                active_buy_countdown = True
                buy_count = 0
                buy_ext_count = 0

            if self.df.iloc[i]['sell_setup_count'] == 9:
                active_sell_countdown = True
                sell_count = 0
                sell_ext_count = 0
                
            # Process Buy Countdown
            if active_buy_countdown and i >= 2:
                if close.iloc[i] <= low.iloc[i-2]:
                    if buy_count < 12:
                        buy_count += 1
                        if buy_count == 8:
                            buy_bar8_close = close.iloc[i]
                        self.df.at[self.df.index[i], 'buy_countdown_count'] = buy_count
                    else:
                        # Qualification for bar 13: Low[13] <= Close[8]
                        if low.iloc[i] <= buy_bar8_close:
                            buy_count = 13
                            self.df.at[self.df.index[i], 'buy_countdown_count'] = 13
                            active_buy_countdown = False
                            buy_count = 0

            # Process Sell Countdown
            if active_sell_countdown and i >= 2:
                if close.iloc[i] >= high.iloc[i-2]:
                    if sell_count < 12:
                        sell_count += 1
                        if sell_count == 8:
                            sell_bar8_close = close.iloc[i]
                        self.df.at[self.df.index[i], 'sell_countdown_count'] = sell_count
                    else:
                        # Qualification for bar 13: High[13] >= Close[8]
                        if high.iloc[i] >= sell_bar8_close:
                            sell_count = 13
                            self.df.at[self.df.index[i], 'sell_countdown_count'] = 13
                            active_sell_countdown = False
                            sell_count = 0
                            
        return self.df

    def calculate_tdst(self) -> pd.DataFrame:
        """
        Calculate TDST (TD Setup Trend) lines.
        Resistance: High of Bar 1 of a Buy Setup (Downtrend).
        Support: Low of Bar 1 of a Sell Setup (Uptrend).
        """
        high = self.df['High']
        low = self.df['Low']
        
        self.df['tdst_support'] = np.nan
        self.df['tdst_resistance'] = np.nan
        
        last_support = np.nan
        last_resistance = np.nan
        
        # Track pending levels from count 1
        pending_support = np.nan
        pending_resistance = np.nan
        
        for i in range(len(self.df)):
            # Buy Setup (Bearish) -> Resistance (High of Bar 1)
            if self.df.iloc[i]['buy_setup_count'] == 1:
                pending_resistance = high.iloc[i]
            
            # Sell Setup (Bullish) -> Support (Low of Bar 1)
            if self.df.iloc[i]['sell_setup_count'] == 1:
                pending_support = low.iloc[i]
            
            # Commit level at count 9
            if self.df.iloc[i]['buy_setup_count'] == 9:
                last_resistance = pending_resistance
            
            if self.df.iloc[i]['sell_setup_count'] == 9:
                last_support = pending_support
                
            self.df.at[self.df.index[i], 'tdst_support'] = last_support
            self.df.at[self.df.index[i], 'tdst_resistance'] = last_resistance
            
        return self.df

    def calculate_recommendations(self) -> pd.DataFrame:
        """
        Generate trading recommendations based on DeMark rules:
        - BUY: Setup 9/Countdown 13 + Oversold (Price < BB Lower) OR Break above TDST Resistance.
        - SELL: Setup 9/Countdown 13 + Overbought (Price > BB Upper) OR Break below TDST Support.
        """
        self.df['recommendation'] = 'HOLD'
        
        for i in range(len(self.df)):
            close = self.df.iloc[i]['Close']
            support = self.df.iloc[i]['tdst_support']
            resist = self.df.iloc[i]['tdst_resistance']
            bb_upper = self.df.iloc[i]['bb_upper']
            bb_lower = self.df.iloc[i]['bb_lower']
            
            s_9 = self.df.iloc[i]['sell_setup_count'] == 9
            b_9 = self.df.iloc[i]['buy_setup_count'] == 9
            s_13 = self.df.iloc[i]['sell_countdown_count'] == 13
            b_13 = self.df.iloc[i]['buy_countdown_count'] == 13
            
            rec = "HOLD"
            
            # SELL SIGNALS
            if s_9 or s_13:
                if close > bb_upper:
                    rec = "SELL (Overbought)"
                else:
                    rec = "SELL (Setup Complete)"
            
            # Support break is a strong sell (Only on the crossover bar)
            if not np.isnan(support) and i > 0:
                prev_close = self.df.iloc[i-1]['Close']
                if close < support and prev_close >= support:
                    rec = "SELL (Support Break)"
                
            # BUY SIGNALS
            if b_9 or b_13:
                if close < bb_lower:
                    rec = "BUY (Oversold)"
                else:
                    rec = "BUY (Setup Complete)"
                    
            # Resistance break is a strong buy (Only on the crossover bar)
            if not np.isnan(resist) and i > 0:
                prev_close = self.df.iloc[i-1]['Close']
                if close > resist and prev_close <= resist:
                    rec = "BUY (Resistance Break)"
                
            self.df.at[self.df.index[i], 'recommendation'] = rec
            
        return self.df

    def calculate_bollinger_bands(self, period: int = 20, std_dev: float = 2.0) -> pd.DataFrame:
        """
        Calculate Bollinger Bands.
          bb_middle = rolling SMA(period)
          bb_upper  = bb_middle + std_dev * rolling_std
          bb_lower  = bb_middle - std_dev * rolling_std
        """
        close = self.df['Close']
        self.df['bb_middle'] = close.rolling(period).mean()
        rolling_std = close.rolling(period).std()
        self.df['bb_upper'] = self.df['bb_middle'] + std_dev * rolling_std
        self.df['bb_lower'] = self.df['bb_middle'] - std_dev * rolling_std
        return self.df

    def run_all(self) -> pd.DataFrame:
        """Run all DeMark calculations in sequence."""
        self.calculate_setup()
        self.validate_intersection()
        self.calculate_countdown()
        self.calculate_tdst()
        self.calculate_bollinger_bands()
        self.calculate_recommendations()
        return self.df
