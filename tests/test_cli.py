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


def _results_frame_with_setup_nines():
    index = pd.date_range("2023-01-01", periods=4)
    return pd.DataFrame(
        {
            "Close": [100.0, 101.0, 102.0, 103.0],
            "buy_setup_count": [0, 9, 0, 0],
            "sell_setup_count": [0, 0, 9, 0],
            "buy_countdown_count": [0, 0, 0, 0],
            "sell_countdown_count": [0, 0, 0, 0],
            "tdst_support": [99.0, 99.0, 99.0, 99.0],
            "tdst_resistance": [104.0, 104.0, 104.0, 104.0],
            "recommendation": ["HOLD", "BUY", "SELL", "HOLD"],
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
    mock_plot_results.assert_called_once_with(results, "AAPL", output_mode="png")


@patch("demark.cli.plot_results")
@patch("demark.cli.save_to_csv")
@patch("demark.cli.DeMarkEngine")
@patch("demark.cli.YFinanceProvider")
@patch(
    "sys.argv",
    [
        "demark",
        "--ticker",
        "AAPL",
        "--period",
        "1mo",
        "--plot",
        "--plot-output-mode",
        "both",
        "--no-save",
    ],
)
def test_cli_no_save_with_plot_uses_selected_output_mode(
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
    mock_plot_results.assert_called_once_with(results, "AAPL", output_mode="both")


@patch("demark.cli.plot_results")
@patch("demark.cli.save_to_csv")
@patch("demark.cli.DeMarkEngine")
@patch("demark.cli.YFinanceProvider")
@patch("sys.argv", ["demark", "--ticker", "AAPL", "--period", "1mo", "--no-save", "--debug-setups"])
def test_cli_debug_setups_explains_missing_support(
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

    out = capsys.readouterr().out
    assert "Setup diagnostics:" in out
    assert "Sell Setup 9 completions: 0" in out
    assert "TDST Support remains NaN because no Sell Setup 9 completed in this window." in out
    mock_save_to_csv.assert_not_called()
    mock_plot_results.assert_not_called()


def test_print_setup_diagnostics_reports_completed_setups(capsys):
    cli.print_setup_diagnostics(_results_frame_with_setup_nines())
    out = capsys.readouterr().out
    assert "Buy Setup 9 completions: 1" in out
    assert "Sell Setup 9 completions: 1" in out
    assert "Latest Buy Setup 9:" in out
    assert "Latest Sell Setup 9:" in out


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


def _ohlcv_frame(periods=40):
    index = pd.date_range("2023-01-01", periods=periods)
    closes = [100.0 - (i * 0.5) for i in range(periods)]
    return pd.DataFrame(
        {
            "Open": closes,
            "High": [c + 1.0 for c in closes],
            "Low": [c - 1.0 for c in closes],
            "Close": closes,
            "Volume": [1000 + i for i in range(periods)],
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


def test_plot_results_writes_html_file(tmp_path):
    df = _plot_frame()

    cli.plot_results(df, "AAPL", str(tmp_path), output_mode="html")

    html_files = list(tmp_path.glob("AAPL_*.html"))
    png_files = list(tmp_path.glob("AAPL_*.png"))
    assert len(html_files) == 1
    assert len(png_files) == 0
    content = html_files[0].read_text(encoding="utf-8")
    assert "<html" in content.lower()
    assert "plotly" in content.lower()


def test_plot_results_writes_both_html_and_png_files(tmp_path):
    df = _plot_frame()

    cli.plot_results(df, "AAPL", str(tmp_path), output_mode="both")

    html_files = list(tmp_path.glob("AAPL_*.html"))
    png_files = list(tmp_path.glob("AAPL_*.png"))
    assert len(html_files) == 1
    assert len(png_files) == 1
    assert png_files[0].stat().st_size > 0


@patch("demark.cli.YFinanceProvider.fetch_data")
@patch("sys.argv", ["demark", "--ticker", "AAPL", "--period", "1mo", "--plot"])
def test_cli_e2e_persists_csv_and_plot(mock_fetch, tmp_path, monkeypatch):
    mock_fetch.return_value = _ohlcv_frame()
    monkeypatch.chdir(tmp_path)

    cli.main()

    analysis_dir = tmp_path / "analysis"
    assert analysis_dir.exists()
    assert len(list(analysis_dir.glob("AAPL_*.csv"))) == 1
    png_files = list(analysis_dir.glob("AAPL_*.png"))
    assert len(png_files) == 1
    assert png_files[0].stat().st_size > 0


@patch("demark.cli.YFinanceProvider.fetch_data")
@patch(
    "sys.argv",
    [
        "demark",
        "--ticker",
        "AAPL",
        "--period",
        "1mo",
        "--plot",
        "--plot-output-mode",
        "html",
    ],
)
def test_cli_e2e_persists_html_only_when_selected(mock_fetch, tmp_path, monkeypatch):
    mock_fetch.return_value = _ohlcv_frame()
    monkeypatch.chdir(tmp_path)

    cli.main()

    analysis_dir = tmp_path / "analysis"
    assert analysis_dir.exists()
    assert len(list(analysis_dir.glob("AAPL_*.csv"))) == 1
    assert len(list(analysis_dir.glob("AAPL_*.html"))) == 1
    assert len(list(analysis_dir.glob("AAPL_*.png"))) == 0


@patch("demark.cli.YFinanceProvider.fetch_data")
@patch("sys.argv", ["demark", "--ticker", "AAPL", "--period", "1mo", "--plot", "--no-save"])
def test_cli_e2e_no_save_plot_writes_png_in_cwd_only(mock_fetch, tmp_path, monkeypatch):
    mock_fetch.return_value = _ohlcv_frame()
    monkeypatch.chdir(tmp_path)

    cli.main()

    assert not (tmp_path / "analysis").exists()
    png_files = list(tmp_path.glob("AAPL_*.png"))
    assert len(png_files) == 1
    assert png_files[0].stat().st_size > 0


@patch("demark.cli.YFinanceProvider.fetch_data")
@patch(
    "sys.argv",
    [
        "demark",
        "--ticker",
        "AAPL",
        "--period",
        "1mo",
        "--plot",
        "--plot-output-mode",
        "html",
        "--no-save",
    ],
)
def test_cli_e2e_no_save_plot_writes_html_in_cwd_only(mock_fetch, tmp_path, monkeypatch):
    mock_fetch.return_value = _ohlcv_frame()
    monkeypatch.chdir(tmp_path)

    cli.main()

    assert not (tmp_path / "analysis").exists()
    html_files = list(tmp_path.glob("AAPL_*.html"))
    assert len(html_files) == 1
    assert len(list(tmp_path.glob("AAPL_*.png"))) == 0