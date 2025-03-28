import marimo

__generated_with = "0.11.25"
app = marimo.App(
    width="full",
    app_title="Time_Series_Ingestio",
    auto_download=["ipynb"],
)


@app.cell
def _(mo):
    mo.md("It's dangerous to go alone! Take these tools!").callout(kind="warn")
    return


@app.cell
def _():
    from sqlalchemy import create_engine
    import sqlalchemy
    import os
    import pandas
    import marimo as mo
    import polars as pl

    password = "sun"
    DATABASE_URL = f"postgresql://dpv:{password}@34.73.180.136:5432/fsecdatabase"
    engine = create_engine(DATABASE_URL)
    return (
        DATABASE_URL,
        create_engine,
        engine,
        mo,
        os,
        pandas,
        password,
        pl,
        sqlalchemy,
    )


@app.cell
def _(mo):
    mo.md(
        r"""
        ## Upload Time Series Data To Begin Ingestion
        CSVs and TXTs files are currently supported
        """
    )
    return


@app.cell
def _(mo):
    file_browser = mo.ui.file_browser()
    return (file_browser,)


@app.cell
def _(file_browser):
    file_browser
    return


@app.cell
def _(file_browser, pandas):
    df = pandas.read_csv(file_browser.value[0].path)
    return (df,)


@app.cell
def _(mo):
    mo.md("""## Review the Data and Ensure there is a Primary Key or Time Stamps""")
    return


@app.cell
def _(file_browser):
    dataset_name = str(file_browser.value[0].path).split(".")[0].split("\\", 2)[-1]
    return (dataset_name,)


@app.cell
def _(mo):
    mo.md("""### Students do some kind of prilimanary analysis or data cleaning""")
    return


@app.cell
def _(df, mo):
    mo.ui.dataframe(df)
    return


@app.cell
def _():
    # Manual method of reading in CSV
    return


@app.cell
def _(mo):
    mo.md("""## Write the Data to Postgres for Persistance and Ontology Development""")
    return


@app.cell
def _(df, pl):
    new_ts_data = pl.from_pandas(df)  # Convert to polars because future
    return (new_ts_data,)


@app.cell
def _(dataset_name, engine, new_ts_data):
    new_ts_data.write_database(f"time_series.{dataset_name}", engine)
    return


@app.cell
def _(new_ts_data):
    print(type(new_ts_data))
    return


@app.cell
def _(mo):
    mo.md("Hooray, you did it! The Data is saved in postgres").callout(
        kind="success"
    )
    return


if __name__ == "__main__":
    app.run()
