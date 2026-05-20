import pandas as pd
from demark.engine import DeMarkEngine

def test_buy_setup_with_price_flip():
    # Setup requires a flip: close[i-1] >= close[i-5] and close[i] < close[i-4]
    dates = pd.date_range("2023-01-01", periods=15)
    # Price flip at bar 5: close[4]=100 >= close[0]=100, close[5]=90 < close[1]=100
    prices = [100, 100, 100, 100, 100, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81]
    df = pd.DataFrame({"Close": prices, "Low": [p-1 for p in prices], "High": [p+1 for p in prices]}, index=dates)
    engine = DeMarkEngine(df)
    results = engine.calculate_setup()
    
    # Bar 5 should have count 1
    assert results.iloc[5]['buy_setup_count'] == 1
    # Bar 13 should have count 9 (13 = 5 + 8)
    assert results.iloc[13]['buy_setup_count'] == 9

def test_setup_perfection():
    dates = pd.date_range("2023-01-01", periods=15)
    prices = [100, 100, 100, 100, 100, 90, 89, 88, 87, 86, 85, 84, 83, 82, 81]
    # At index 13 (count 9): Close[13]=82.
    # Perfection: min(Low[13], Low[12]) <= min(Low[11], Low[10])
    # Lows: 99, 99, 99, 99, 99, 89, 88, 87, 86, 85, 84, 83, 82, 70, 69
    lows =   [99,  99,  99,  99,  99,  89, 88, 87, 86, 85, 84, 83, 82, 70, 69]
    df = pd.DataFrame({"Close": prices, "Low": lows, "High": [p+1 for p in prices]}, index=dates)
    engine = DeMarkEngine(df)
    results = engine.calculate_setup()
    
    assert results.iloc[13]['buy_setup_count'] == 9
    assert bool(results.iloc[13]['buy_perfect']) is True

def test_tdst_resistance_bar1():
    # Buy Setup (Downtrend) defines Resistance (High of Bar 1)
    dates = pd.date_range("2023-01-01", periods=15)
    prices = [100]*5 + [90, 89, 88, 87, 86, 85, 84, 83, 82, 81]
    highs =  [101]*5 + [91, 90, 89, 88, 87, 86, 85, 84, 83, 82] # High at bar 5 (Setup 1) is 91
    df = pd.DataFrame({"Close": prices, "Low": [p-1 for p in prices], "High": highs}, index=dates)
    engine = DeMarkEngine(df)
    results = engine.run_all()
    
    # Setup 9 is at index 13
    assert results.iloc[13]['buy_setup_count'] == 9
    assert results.iloc[13]['tdst_resistance'] == 91.0

def test_tdst_support_bar1():
    # Sell Setup (Uptrend) defines Support (Low of Bar 1)
    dates = pd.date_range("2023-01-01", periods=15)
    prices = [100]*5 + [110, 111, 112, 113, 114, 115, 116, 117, 118, 119]
    lows =   [99]*5 + [109, 110, 111, 112, 113, 114, 115, 116, 117, 118] # Low at bar 5 (Setup 1) is 109
    df = pd.DataFrame({"Close": prices, "Low": lows, "High": [p+1 for p in prices]}, index=dates)
    engine = DeMarkEngine(df)
    results = engine.run_all()
    
    # Setup 9 is at index 13
    assert results.iloc[13]['sell_setup_count'] == 9
    assert results.iloc[13]['tdst_support'] == 109.0

def test_countdown_qualification():
    # Countdown 13 requires Close[13] <= Close[8]
    n = 100
    dates = pd.date_range("2023-01-01", periods=n)
    # 1. Complete Setup (starts at 5, ends at 13)
    # Drop sharply to ensure Close <= Low[i-2]
    # Low[i-2] = Close[i-2] - 0.1
    # So we need Close[i] <= Close[i-2] - 0.1
    prices = [100]*5 + [90 - i for i in range(n-5)]
    df = pd.DataFrame({"Close": prices, "Low": [p-0.1 for p in prices], "High": [p+0.1 for p in prices]}, index=dates)
    engine = DeMarkEngine(df)
    results = engine.run_all()
    
    # Check CD 13 exists
    cd13_exists = (results['buy_countdown_count'] == 13).any()
    assert cd13_exists

def test_recommendation_crossover():
    # Price breaks resistance at index 18, should HOLD after that
    dates = pd.date_range("2023-01-01", periods=29)
    
    # 1. Price Flip for Buy Setup: Close[i-1] >= Close[i-5] and Close[i] < Close[i-4]
    # Indices 0-4: 100
    # Index 5: 90 (Flip! 100 >= 100, 90 < 100). Setup Count 1.
    prices = [100]*5 + [90, 89, 88, 87, 86, 85, 84, 83, 82] # Setup 9 finishes at index 13
    highs =  [101]*5 + [91, 90, 89, 88, 87, 86, 85, 84, 83] # Bar 1 High at index 5 is 91
    
    # Resistance should be 91.0
    # Bars 14-29: Price rises to break 91.0
    # 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92 (Break!), 93...
    prices += [83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97]
    highs  += [84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98]
    
    df = pd.DataFrame({"Close": prices, "Low": [p-1 for p in prices], "High": highs}, index=dates)
    engine = DeMarkEngine(df)
    results = engine.run_all()
    
    # Setup 9 at index 13
    assert results.iloc[13]['buy_setup_count'] == 9
    assert results.iloc[13]['tdst_resistance'] == 91.0
    
    # Find break index (Price 92 at index 14+9 = 23?)
    # Index 23: 92 > 91. Index 22: 91 <= 91.
    assert results.iloc[23]['Close'] == 92
    assert results.iloc[23]['recommendation'] == "BUY (Resistance Break)"
    assert results.iloc[24]['recommendation'] != "BUY (Resistance Break)"


def _make_buy_setup_df(n_extra=30):
    """
    Helper: 9-bar Buy Setup ending at index 13, followed by n_extra more bars.
    Lows = Close - 1.  Highs = Close + 1.  All floats.
    """
    setup_closes = [100.0]*5 + [90.0 - i for i in range(9)]  # last = 81.0
    last = setup_closes[-1]
    extra_closes = [last - (i + 1.0) for i in range(n_extra)]
    closes = setup_closes + extra_closes
    n = len(closes)
    dates = pd.date_range("2023-01-01", periods=n)
    lows   = [c - 1.0 for c in closes]
    highs  = [c + 1.0 for c in closes]
    return pd.DataFrame({"Close": closes, "Low": lows, "High": highs}, index=dates)


def test_buy_countdown_bar13_uses_low():
    """
    Task 1.1 — Bar 13 qualification must use Low[13] <= Close[8], not Close[13].

    Inject a candidate bar where:
      Close > Close[8]  → OLD close-based check FAILS
      Low   <= Close[8] → NEW low-based check PASSES

    Dataframe is truncated after the candidate so no later bar can satisfy
    the old check and produce a false positive.
    """
    # n_extra=14 → indices 14..27; bar 8 at idx 20, bar 12 at idx 24, candidate at idx 25
    df = _make_buy_setup_df(n_extra=14)
    engine = DeMarkEngine(df)
    engine.calculate_setup()

    # bar8_close: count starts at idx 13 (setup=9), bar 8 is at idx 13+7=20
    bar8_idx = 20
    buy_bar8_close = df.iloc[bar8_idx]['Close']   # 75.0 (81 - 6 = 75; close[13]=82,14=80,...,20=75 - trace confirmed)

    candidate_idx = 25   # bar 12 at idx 24, bar 13 candidate at idx 25

    df_mod = df.copy()
    # close > bar8_close → OLD check (close <= bar8) FAILS
    df_mod.at[df_mod.index[candidate_idx], 'Close'] = buy_bar8_close + 0.5   # 75.5
    # low <= bar8_close → NEW check (low <= bar8) PASSES
    df_mod.at[df_mod.index[candidate_idx], 'Low']   = buy_bar8_close - 0.5   # 74.5
    # Ensure counting cond: close[25] <= low[23]; raise low[23]
    df_mod.at[df_mod.index[candidate_idx - 2], 'Low'] = buy_bar8_close + 1.0  # 76.0 >= 75.5 ✓

    # Truncate: only up to and including the candidate — no later bars to smuggle a pass
    df_mod = df_mod.iloc[:candidate_idx + 1]

    engine2 = DeMarkEngine(df_mod)
    engine2.calculate_setup()
    engine2.calculate_countdown()
    results = engine2.df

    assert (results['buy_countdown_count'] == 13).any(), (
        f"Buy countdown 13 did not fire. Low-based check should pass "
        f"(low={buy_bar8_close - 0.5} <= bar8_close={buy_bar8_close}). "
        f"Close-based check rejects it (close={buy_bar8_close + 0.5} > bar8_close). "
        f"Fix engine to use Low[13] instead of Close[13]."
    )


def test_sell_countdown_bar13_uses_high():
    """
    Task 1.2 — Bar 13 Sell qualification must use High[13] >= Close[8], not Close[13].

    Inject a candidate bar where:
      Close < Close[8]  → OLD close-based check FAILS
      High  >= Close[8] → NEW high-based check PASSES

    Dataframe truncated after candidate to prevent false positives.
    """
    setup_closes = [100.0]*5 + [110.0 + i for i in range(9)]  # 110..118, setup bar 9 at idx 13
    last = setup_closes[-1]  # 118
    extra_closes = [last + (i + 1.0) for i in range(14)]  # 14 extra bars
    closes = setup_closes + extra_closes

    n = len(closes)
    dates = pd.date_range("2023-01-01", periods=n)
    # Counting cond: close[i] >= high[i-2]; rises 1/bar, high=close+1 → close[i]-close[i-2]=2 >= high offset ✓
    highs = [c + 1.0 for c in closes]
    lows  = [c - 1.0 for c in closes]
    df = pd.DataFrame({"Close": closes, "Low": lows, "High": highs}, index=dates)

    engine = DeMarkEngine(df)
    engine.calculate_setup()

    bar8_idx = 20
    sell_bar8_close = df.iloc[bar8_idx]['Close']   # 118 + 7 = 125.0

    candidate_idx = 25
    df_mod = df.copy()
    # close < sell_bar8_close → OLD check FAILS
    df_mod.at[df_mod.index[candidate_idx], 'Close'] = sell_bar8_close - 0.5   # 124.5
    # high >= sell_bar8_close → NEW check PASSES
    df_mod.at[df_mod.index[candidate_idx], 'High']  = sell_bar8_close + 0.5   # 125.5
    # counting cond: close[25] >= high[23]; lower high[23]
    df_mod.at[df_mod.index[candidate_idx - 2], 'High'] = sell_bar8_close - 1.5  # 123.5 <= 124.5 ✓

    df_mod = df_mod.iloc[:candidate_idx + 1]   # truncate — no later bars

    engine2 = DeMarkEngine(df_mod)
    engine2.calculate_setup()
    engine2.calculate_countdown()
    results = engine2.df

    assert (results['sell_countdown_count'] == 13).any(), (
        f"Sell countdown 13 did not fire. High-based check should pass "
        f"(high={sell_bar8_close + 0.5} >= bar8_close={sell_bar8_close}). "
        f"Close-based check rejects it (close={sell_bar8_close - 0.5} < bar8_close). "
        f"Fix engine to use High[13] instead of Close[13]."
    )


def test_buy_countdown_bar13_waits_then_later_qualifies():
    """
    If the first bar-13 candidate satisfies the counting condition but fails
    the Low[13] <= Close[8] qualifier, the count must stay at 12 until a later
    qualifying bar appears.
    """
    df = _make_buy_setup_df(n_extra=15)
    engine = DeMarkEngine(df)
    engine.calculate_setup()

    bar8_idx = 20
    buy_bar8_close = df.iloc[bar8_idx]['Close']
    first_candidate_idx = 25
    second_candidate_idx = 26

    df_mod = df.copy()

    # First candidate: counting condition passes, qualifier fails -> remain at 12.
    df_mod.at[df_mod.index[first_candidate_idx], 'Close'] = buy_bar8_close + 0.5
    df_mod.at[df_mod.index[first_candidate_idx], 'Low'] = buy_bar8_close + 0.25
    df_mod.at[df_mod.index[first_candidate_idx - 2], 'Low'] = buy_bar8_close + 1.0

    # Second candidate: counting condition passes again, qualifier now passes -> 13.
    df_mod.at[df_mod.index[second_candidate_idx], 'Close'] = buy_bar8_close + 0.25
    df_mod.at[df_mod.index[second_candidate_idx], 'Low'] = buy_bar8_close - 0.5
    df_mod.at[df_mod.index[second_candidate_idx - 2], 'Low'] = buy_bar8_close + 1.0

    engine2 = DeMarkEngine(df_mod)
    engine2.calculate_setup()
    engine2.calculate_countdown()
    results = engine2.df

    assert results.iloc[first_candidate_idx]['buy_countdown_count'] == 0
    assert results.iloc[second_candidate_idx]['buy_countdown_count'] == 13


def test_sell_countdown_bar13_waits_then_later_qualifies():
    """
    If the first sell bar-13 candidate satisfies the counting condition but
    fails the High[13] >= Close[8] qualifier, the count must stay at 12 until
    a later qualifying bar appears.
    """
    setup_closes = [100.0]*5 + [110.0 + i for i in range(9)]
    last = setup_closes[-1]
    extra_closes = [last + (i + 1.0) for i in range(15)]
    closes = setup_closes + extra_closes

    dates = pd.date_range("2023-01-01", periods=len(closes))
    highs = [c + 1.0 for c in closes]
    lows = [c - 1.0 for c in closes]
    df = pd.DataFrame({"Close": closes, "Low": lows, "High": highs}, index=dates)

    engine = DeMarkEngine(df)
    engine.calculate_setup()

    bar8_idx = 20
    sell_bar8_close = df.iloc[bar8_idx]['Close']
    first_candidate_idx = 25
    second_candidate_idx = 26

    df_mod = df.copy()

    # First candidate: counting condition passes, qualifier fails -> remain at 12.
    df_mod.at[df_mod.index[first_candidate_idx], 'Close'] = sell_bar8_close - 0.5
    df_mod.at[df_mod.index[first_candidate_idx], 'High'] = sell_bar8_close - 0.25
    df_mod.at[df_mod.index[first_candidate_idx - 2], 'High'] = sell_bar8_close - 1.0

    # Second candidate: counting condition passes again, qualifier now passes -> 13.
    df_mod.at[df_mod.index[second_candidate_idx], 'Close'] = sell_bar8_close - 0.25
    df_mod.at[df_mod.index[second_candidate_idx], 'High'] = sell_bar8_close + 0.5
    df_mod.at[df_mod.index[second_candidate_idx - 2], 'High'] = sell_bar8_close - 1.0

    engine2 = DeMarkEngine(df_mod)
    engine2.calculate_setup()
    engine2.calculate_countdown()
    results = engine2.df

    assert results.iloc[first_candidate_idx]['sell_countdown_count'] == 0
    assert results.iloc[second_candidate_idx]['sell_countdown_count'] == 13


def test_recycle_columns_always_present():
    """Task 2.1 — buy_countdown_recycled and sell_countdown_recycled must exist."""
    df = _make_buy_setup_df(n_extra=5)
    engine = DeMarkEngine(df)
    engine.calculate_setup()
    engine.calculate_countdown()
    assert 'buy_countdown_recycled' in engine.df.columns
    assert 'sell_countdown_recycled' in engine.df.columns
    assert not engine.df['buy_countdown_recycled'].any()
    assert not engine.df['sell_countdown_recycled'].any()


def test_buy_countdown_recycle():
    """
    Task 2.2 — When an active buy countdown is still open at bar 18+,
    a new completed Buy Setup triggers a Recycle.

    Series design:
      - First Buy Setup completes at idx ~13 (starts countdown).
      - Prices bounce up (interrupting the setup streak), then decline again.
      - Second Buy Setup completes when buy_ext_count > 18.
      → buy_countdown_recycled == True at the second setup bar.
    """
    # Phase 1: first completed setup starts countdown.
    phase1 = [100.0]*5 + [90.0 - i for i in range(9)]  # setup=9 at idx 13
    # Phase 2: interruption (breaks consecutive setup-qualifying closes).
    phase2 = [95.0 + i for i in range(6)]
    # Phase 3: strong decline to create >18 consecutive setup-qualifying closes.
    start = phase2[-1]
    phase3 = [start - 2.0 * (i + 1) for i in range(30)]
    closes = phase1 + phase2 + phase3

    n = len(closes)
    dates = pd.date_range("2023-01-01", periods=n)
    # Keep countdown active (avoid reaching 13) so recycle condition can fire first.
    lows  = [c - 10.0 for c in closes]
    highs = [c + 1.0 for c in closes]
    df = pd.DataFrame({"Close": closes, "Low": lows, "High": highs}, index=dates)

    engine = DeMarkEngine(df)
    engine.calculate_setup()

    setup_bars = engine.df[engine.df['buy_setup_count'] == 9].index.tolist()
    assert len(setup_bars) >= 2, (
        f"Need at least 2 Buy Setup=9 completions to test recycle; got {len(setup_bars)}. "
        f"Check series construction."
    )

    engine.calculate_countdown()
    assert engine.df['buy_countdown_recycled'].any(), (
        "buy_countdown_recycled never fired. A new Buy Setup completing >18 bars "
        "into an active countdown should trigger recycle (reset count, mark column True)."
    )

    recycle_idx = engine.df.index[engine.df['buy_countdown_recycled']].tolist()[0]
    assert engine.df.loc[recycle_idx, 'buy_countdown_count'] == 0


def test_buy_countdown_recycle_threshold_exactly_18_does_not_fire():
    """
    Recycle should trigger only when extension count is > 18, not at 18.
    """
    n = 23  # indices 0..22
    dates = pd.date_range("2023-01-01", periods=n)

    # Strictly descending closes so close[i] < close[i-4] is always true for i >= 4.
    closes = [100.0 - i for i in range(n)]

    # Keep countdown counting condition false so countdown doesn't complete first:
    # buy count needs close[i] <= low[i-2]. With very low lows, this is false.
    lows = [c - 100.0 for c in closes]
    highs = [c + 1.0 for c in closes]

    df = pd.DataFrame({"Close": closes, "Low": lows, "High": highs}, index=dates)
    engine = DeMarkEngine(df)

    # Activate buy countdown at i=4, then 18 consecutive extension bars (i=5..22).
    engine.df['buy_setup_count'] = 0
    engine.df['sell_setup_count'] = 0
    engine.df.at[engine.df.index[4], 'buy_setup_count'] = 9

    engine.calculate_countdown()

    assert not engine.df['buy_countdown_recycled'].any(), (
        "Recycle fired at exactly 18 extension bars, but rule requires > 18."
    )


def test_sell_countdown_recycle_threshold_exactly_18_does_not_fire():
    """
    Recycle should trigger only when extension count is > 18, not at 18.
    Sell-side symmetric boundary.
    """
    n = 23  # indices 0..22
    dates = pd.date_range("2023-01-01", periods=n)

    # Strictly ascending closes so close[i] > close[i-4] is always true for i >= 4.
    closes = [100.0 + i for i in range(n)]

    # Keep sell countdown counting condition false so countdown doesn't complete first:
    # sell count needs close[i] >= high[i-2]. With very high highs, this is false.
    highs = [c + 100.0 for c in closes]
    lows = [c - 1.0 for c in closes]

    df = pd.DataFrame({"Close": closes, "Low": lows, "High": highs}, index=dates)
    engine = DeMarkEngine(df)

    # Activate sell countdown at i=4, then 18 consecutive extension bars (i=5..22).
    engine.df['buy_setup_count'] = 0
    engine.df['sell_setup_count'] = 0
    engine.df.at[engine.df.index[4], 'sell_setup_count'] = 9

    engine.calculate_countdown()

    assert not engine.df['sell_countdown_recycled'].any(), (
        "Sell recycle fired at exactly 18 extension bars, but rule requires > 18."
    )


def test_buy_countdown_recycle_threshold_19_does_fire():
    """
    Recycle should fire once the extension count exceeds 18.
    Buy-side positive boundary at 19 bars.
    """
    n = 24  # indices 0..23
    dates = pd.date_range("2023-01-01", periods=n)

    closes = [100.0 - i for i in range(n)]
    lows = [c - 100.0 for c in closes]
    highs = [c + 1.0 for c in closes]

    df = pd.DataFrame({"Close": closes, "Low": lows, "High": highs}, index=dates)
    engine = DeMarkEngine(df)

    engine.df['buy_setup_count'] = 0
    engine.df['sell_setup_count'] = 0
    engine.df.at[engine.df.index[4], 'buy_setup_count'] = 9

    engine.calculate_countdown()

    assert engine.df['buy_countdown_recycled'].any(), (
        "Buy recycle did not fire at 19 extension bars, but rule requires recycle at > 18."
    )
    recycle_idx = engine.df.index[engine.df['buy_countdown_recycled']].tolist()[0]
    assert recycle_idx == engine.df.index[23]


def test_sell_countdown_recycle_threshold_19_does_fire():
    """
    Recycle should fire once the extension count exceeds 18.
    Sell-side positive boundary at 19 bars.
    """
    n = 24  # indices 0..23
    dates = pd.date_range("2023-01-01", periods=n)

    closes = [100.0 + i for i in range(n)]
    highs = [c + 100.0 for c in closes]
    lows = [c - 1.0 for c in closes]

    df = pd.DataFrame({"Close": closes, "Low": lows, "High": highs}, index=dates)
    engine = DeMarkEngine(df)

    engine.df['buy_setup_count'] = 0
    engine.df['sell_setup_count'] = 0
    engine.df.at[engine.df.index[4], 'sell_setup_count'] = 9

    engine.calculate_countdown()

    assert engine.df['sell_countdown_recycled'].any(), (
        "Sell recycle did not fire at 19 extension bars, but rule requires recycle at > 18."
    )
    recycle_idx = engine.df.index[engine.df['sell_countdown_recycled']].tolist()[0]
    assert recycle_idx == engine.df.index[23]


def test_countdown_not_reset_by_second_setup_9():
    """
    Regression: a second same-direction Setup 9 that does NOT cross the recycle
    threshold (extension < 18 bars) must NOT reset an in-progress countdown.

    Spec: openspec/specs/countdown-recycle/spec.md
          "New setup under 18 bars does not recycle"

    Series construction
    -------------------
    idx  0-4   flat 100 (no setup yet)
    idx  5-13  decline 90→82  → first Buy Setup-9 at idx 13
    idx 14-16  continue declining 81,80,79 → countdown advances to 3
    idx 17-22  sharp bounce 100→105       → setup streak breaks, countdown pauses
    idx 23-31  decline 94→86 with price flip at 23 → second Buy Setup-9 at idx 31
    idx 32-35  tail

    Pre-fix behaviour: buy_count reset to 0 at idx 31 → df shows 1 on that bar.
    Post-fix behaviour: count continues uninterrupted → df shows 12 on that bar,
                        13 on idx 32 (bar-13 qualification also passes).
    """
    closes = (
        [100.0] * 5 +
        [90.0 - i for i in range(9)] +       # first Setup-9 at idx 13
        [81.0, 80.0, 79.0] +                 # countdown ticks 1-3; setup extends past 9
        [100.0 + i for i in range(6)] +      # bounce; breaks setup streak
        [94.0 - i for i in range(9)] +       # second Setup-9 at idx 31
        [85.0 - i for i in range(4)]         # tail
    )
    dates = pd.date_range("2023-01-01", periods=len(closes))
    lows  = [c - 1.0 for c in closes]
    highs = [c + 1.0 for c in closes]
    df = pd.DataFrame({"Close": closes, "Low": lows, "High": highs}, index=dates)

    engine = DeMarkEngine(df)
    engine.calculate_setup()

    setup9_positions = [i for i, v in enumerate(engine.df['buy_setup_count']) if v == 9]
    assert setup9_positions == [13, 31], (
        f"Series must produce Buy Setup-9 at exactly idx 13 and 31; got {setup9_positions}"
    )

    engine.calculate_countdown()
    results = engine.df

    # At idx 30 the count must be 12 (not yet qualified as bar 13) — same in both pre/post-fix.
    assert results.iloc[30]['buy_countdown_count'] == 12, (
        f"Expected 12 at idx 30, got {results.iloc[30]['buy_countdown_count']}."
    )
    # At the second Setup-9 bar (idx 31) the count must complete to 13, not reset to 1.
    # Pre-fix: buy_count was reset to 0 then advanced to 1 → df shows 1.
    # Post-fix: count continues from 12 and bar-13 qualification passes → df shows 13.
    assert results.iloc[31]['buy_countdown_count'] == 13, (
        f"Expected 13 at second Setup-9 bar (countdown completion), "
        f"got {results.iloc[31]['buy_countdown_count']}. "
        f"A result of 1 reproduces the bug: countdown was unconditionally reset on Setup-9."
    )
    # Recycle must not have fired (only 9 extension bars, well under 18).
    assert not results['buy_countdown_recycled'].any(), (
        "Recycle must not fire — extension was 9 bars, under the 18-bar threshold."
    )
