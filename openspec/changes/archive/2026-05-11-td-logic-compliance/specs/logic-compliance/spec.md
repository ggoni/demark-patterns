### Requirement: TDST Line Definition
The CLI SHALL calculate TDST Support as the `Low` of the **first bar** (count 1) of a completed Sell Setup, and TDST Resistance as the `High` of the **first bar** (count 1) of a completed Buy Setup.

### Requirement: Price Flip
A TD Setup SHALL only begin if a "Price Flip" occurs.
- **Buy Setup Start**: `close[i-1] >= close[i-5]` AND `close[i] < close[i-4]`.
- **Sell Setup Start**: `close[i-1] <= close[i-5]` AND `close[i] > close[i-4]`.

### Requirement: Setup Perfection
A TD Setup SHALL be flagged as "Perfected" only if:
- **Buy**: `min(Low[8], Low[9]) <= min(Low[6], Low[7])`.
- **Sell**: `max(High[8], High[9]) >= max(High[6], High[7])`.

### Requirement: Countdown Qualification
A TD Countdown SHALL only complete (reach 13) if the close of bar 13 qualifies:
- **Buy**: `Close[13] <= Close[8]`.
- **Sell**: `Close[13] >= Close[8]`.
If bar 13 does not qualify, the count SHALL remain at 12 until a qualifying bar appears.
