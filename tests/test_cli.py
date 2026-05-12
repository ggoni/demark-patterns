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


@patch("demark.cli.DeMarkEngine")
@patch("demark.cli.YFinanceProvider")
@patch("sys.argv", ["demark", "--ticker", "AAPL", "--period", "1mo"])
def test_cli_prints_error_and_exits_on_fetch_failure(
    mock_provider_cls,
    mock_engine_cls,
    capsys,
):
    provider = mock_provider_cls.return_value
    provider.fetch_data.side_effect = Exception("network down")

    cli.main()

    mock_engine_cls.assert_not_called()
    assert "Error: network down" in capsys.readouterr().out


def _plot_frame():
    index = pd.date_range("2023-01-01", periods=5)
    return pd.DataFrame(
        {
            "Close": [100.0, 101.0, 102.0, 101.5, 103.0],
            "Low": [99.0, 100.0, 101.0, 100.5, 102.0],
            "High": [101.0, 102.0, 103.0, 102.5, 104.0],
            "buy_setup_count": [0, 1, 0, 0, 0],
            "sell_setup_count": [0, 0, 1, 0, 0],
            "buy_countdown_count": [0, 0, 1, 0, 0],
            "sell_countdown_count": [0, 0, 0, 1, 0],
            "tdst_support": [98.5, 98.5, 98.5, 98.5, 98.5],
            "tdst_resistance": [104.5, 104.5, 104.5, 104.5, 104.5],
        },
        index=index,
    )


def test_save_to_csv_writes_output_file(tmp_path):
    df = _results_frame()

    cli.save_to_csv(df, "AAPL", str(tmp_path))

    files = list(tmp_path.glob("AAPL_*.csv"))
    assert len(files) == 1
    written = pd.read_csv(files[0], index_col=0)
    assert len(written) == len(df)


def test_plot_results_writes_png_file(tmp_path):
    df = _plot_frame()

    cli.plot_results(df, "AAPL", str(tmp_path))

    files = list(tmp_path.glob("AAPL_*.png"))
    assert len(files) == 1
    assert files[0].stat().st_size > 0