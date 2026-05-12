import pandas as pd
from unittest.mock import patch

from demark import cli


def _results_frame():
    index = pd.date_range("2023-01-01", periods=3)
    return pd.DataFrame(
        {
            "Close": [100.0, 101.0, 102.0],
            "buy_setup_count": [0, 0, 0],
            "sell_setup_count": [0, 0, 0],
            "buy_countdown_count": [0, 0, 0],
            "sell_countdown_count": [0, 0, 0],
            "tdst_support": [99.0, 99.0, 99.0],
            "tdst_resistance": [103.0, 103.0, 103.0],
            "recommendation": ["HOLD", "HOLD", "BUY"],
        },
        index=index,
    )


@patch("demark.cli.plot_results")
@patch("demark.cli.save_to_csv")
@patch("demark.cli.DeMarkEngine")
@patch("demark.cli.YFinanceProvider")
@patch("sys.argv", ["demark", "--ticker", "AAPL", "--period", "1mo", "--no-save"])
def test_cli_no_save_skips_persistence(
    mock_provider_cls,
    mock_engine_cls,
    mock_save_to_csv,
    mock_plot_results,
    capsys,
):
    provider = mock_provider_cls.return_value
    provider.fetch_data.return_value = pd.DataFrame({"Close": [100.0]})

    engine = mock_engine_cls.return_value
    engine.run_all.return_value = _results_frame()

    cli.main()

    mock_save_to_csv.assert_not_called()
    mock_plot_results.assert_not_called()
    assert "RECOMMENDATION:" in capsys.readouterr().out


@patch("demark.cli.plot_results")
@patch("demark.cli.save_to_csv")
@patch("demark.cli.DeMarkEngine")
@patch("demark.cli.YFinanceProvider")
@patch("sys.argv", ["demark", "--ticker", "AAPL", "--period", "1mo", "--plot", "--no-save"])
def test_cli_no_save_with_plot_skips_csv_only(
    mock_provider_cls,
    mock_engine_cls,
    mock_save_to_csv,
    mock_plot_results,
):
    provider = mock_provider_cls.return_value
    provider.fetch_data.return_value = pd.DataFrame({"Close": [100.0]})

    engine = mock_engine_cls.return_value
    results = _results_frame()
    engine.run_all.return_value = results

    cli.main()

    mock_save_to_csv.assert_not_called()
    mock_plot_results.assert_called_once_with(results, "AAPL")