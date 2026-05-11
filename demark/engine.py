import pandas as pd
import numpy as np

class DeMarkEngine:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def calculate_setup(self) -> pd.DataFrame:
        """
        Calculate TD Setup (9-count).
        Buy Setup: Close < Close.shift(4) for 9 consecutive bars.
        Sell Setup: Close > Close.shift(4) for 9 consecutive bars.
        """
        # Buy Setup
        self.df['buy_setup_cond'] = self.df['Close'] < self.df['Close'].shift(4)
        self.df['buy_setup_count'] = 0
        
        count = 0
        counts = []
        for val in self.df['buy_setup_cond']:
            if val:
                count += 1
            else:
                count = 0
            counts.append(count)
        self.df['buy_setup_count'] = counts
        
        # Sell Setup
        self.df['sell_setup_cond'] = self.df['Close'] > self.df['Close'].shift(4)
        self.df['sell_setup_count'] = 0
        
        count = 0
        counts = []
        for val in self.df['sell_setup_cond']:
            if val:
                count += 1
            else:
                count = 0
            counts.append(count)
        self.df['sell_setup_count'] = counts
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
        Starts after a completed Setup (9-count).
        Buy Countdown: Close <= Low[n-2]
        Sell Countdown: Close >= High[n-2]
        """
        self.df['buy_countdown_count'] = 0
        self.df['sell_countdown_count'] = 0
        
        # We need to track active countdowns
        active_buy_countdown = False
        buy_count = 0
        
        active_sell_countdown = False
        sell_count = 0
        
        for i in range(len(self.df)):
            # Check for Setup completion to start/reset countdown
            if self.df.iloc[i]['buy_setup_count'] == 9:
                active_buy_countdown = True
                buy_count = 0 # Reset or start new
            
            if self.df.iloc[i]['sell_setup_count'] == 9:
                active_sell_countdown = True
                sell_count = 0
                
            # Process Buy Countdown
            if active_buy_countdown and i >= 2:
                if self.df.iloc[i]['Close'] <= self.df.iloc[i-2]['Low']:
                    buy_count += 1
                    self.df.at[self.df.index[i], 'buy_countdown_count'] = buy_count
                    if buy_count == 13:
                        active_buy_countdown = False
                        buy_count = 0

            # Process Sell Countdown
            if active_sell_countdown and i >= 2:
                if self.df.iloc[i]['Close'] >= self.df.iloc[i-2]['High']:
                    sell_count += 1
                    self.df.at[self.df.index[i], 'sell_countdown_count'] = sell_count
                    if sell_count == 13:
                        active_sell_countdown = False
                        sell_count = 0
                        
        return self.df
    def calculate_tdst(self) -> pd.DataFrame:
        """
        Calculate TDST (TD Setup Trend) lines.
        Resistance: Highest high of a Sell Setup.
        Support: Lowest low of a Buy Setup.
        """
        self.df['tdst_support'] = np.nan
        self.df['tdst_resistance'] = np.nan
        
        last_support = np.nan
        last_resistance = np.nan
        
        for i in range(len(self.df)):
            # Update Support on Buy Setup completion
            if self.df.iloc[i]['buy_setup_count'] == 9:
                setup_range = self.df.iloc[i-8 : i+1]
                last_support = setup_range['Low'].min()
            
            # Update Resistance on Sell Setup completion
            if self.df.iloc[i]['sell_setup_count'] == 9:
                setup_range = self.df.iloc[i-8 : i+1]
                last_resistance = setup_range['High'].max()
                
            self.df.at[self.df.index[i], 'tdst_support'] = last_support
            self.df.at[self.df.index[i], 'tdst_resistance'] = last_resistance
            
        return self.df
    
    def run_all(self) -> pd.DataFrame:
        """Run all DeMark calculations in sequence."""
        self.calculate_setup()
        self.validate_intersection()
        self.calculate_countdown()
        self.calculate_tdst()
        return self.df
