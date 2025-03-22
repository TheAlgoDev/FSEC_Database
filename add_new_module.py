import marimo

__generated_with = "0.11.25"
app = marimo.App(width="medium")


@app.cell
def _():
    import os
    import marimo as mo
    from sqlalchemy import create_engine, inspect
    from sqlalchemy.dialects.postgresql import insert as pg_insert
    from sqlalchemy import create_engine, Table, Column, MetaData, insert

    return (
        Column,
        MetaData,
        Table,
        create_engine,
        insert,
        inspect,
        mo,
        os,
        pg_insert,
    )


@app.cell
def _(MetaData, create_engine, inspect, os):
    password = os.environ.get("POSTGRES_PASSWORD", "sun")
    DATABASE_URL = f"postgresql://dpv:{password}@34.73.180.136:5432/fsecdatabase"
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    metadata = MetaData()


    print(inspector.get_schema_names())  # See all schemas

    return DATABASE_URL, engine, inspector, metadata, password


@app.cell
def _(engine, instrument_data, mo, module_metadata):
    _df = mo.sql(
        f"""
        SELECT * FROM instrument_data.module_metadata
        """,
        engine=engine
    )
    return


@app.cell
def _(mo):
    form = (
        mo.md(
            """
            ### Module Metadata Entry

            {module_id}
            {serial_number}
            {make}
            {model}
            {nameplate_pmp}
            {nameplate_vmp}
            {nameplate_imp}
            {nameplate_voc}
            {nameplate_isc}
            {temperature_coefficient_voltage}
            {temperature_coefficient_power}
            {temperature_coefficient_current}
            {module_packaging}
            {interconnection_scheme}
            {number_parallel_strings}
            {cells_per_string}
            {module_arc}
            {connector_type}
            {junction_box_locations}
            {number_junction_box}
            {number_busbars}
            {cell_area}
            {module_area}
            {cell_technology}
            {wafer_doping_polarity}
            {wafer_crystallinity}
            {encapsulant}
            {backsheet}
            {frame_material}
            {x}
            {y}
            """
        )
        .batch(
            module_id=mo.ui.text(label="Module ID (required)"),
            serial_number=mo.ui.text(label="Serial Number"),
            make=mo.ui.text(label="Make"),
            model=mo.ui.text(label="Model"),
            nameplate_pmp=mo.ui.number(label="Nameplate Pmp"),
            nameplate_vmp=mo.ui.number(label="Nameplate Vmp"),
            nameplate_imp=mo.ui.number(label="Nameplate Imp"),
            nameplate_voc=mo.ui.number(label="Nameplate Voc"),
            nameplate_isc=mo.ui.number(label="Nameplate Isc"),
            temperature_coefficient_voltage=mo.ui.text(label="Temp Coefficient Voltage"),
            temperature_coefficient_power=mo.ui.text(label="Temp Coefficient Power"),
            temperature_coefficient_current=mo.ui.text(label="Temp Coefficient Current"),
            module_packaging=mo.ui.text(label="Module Packaging"),
            interconnection_scheme=mo.ui.text(label="Interconnection Scheme"),
            number_parallel_strings=mo.ui.text(label="Number of Parallel Strings"),
            cells_per_string=mo.ui.text(label="Cells per String"),
            module_arc=mo.ui.text(label="Module Arc"),
            connector_type=mo.ui.text(label="Connector Type"),
            junction_box_locations=mo.ui.text(label="Junction Box Locations"),
            number_junction_box=mo.ui.text(label="Number of Junction Boxes"),
            number_busbars=mo.ui.text(label="Number of Busbars"),
            cell_area=mo.ui.text(label="Cell Area"),
            module_area=mo.ui.text(label="Module Area"),
            cell_technology=mo.ui.text(label="Cell Technology"),
            wafer_doping_polarity=mo.ui.text(label="Wafer Doping Polarity"),
            wafer_crystallinity=mo.ui.text(label="Wafer Crystallinity"),
            encapsulant=mo.ui.text(label="Encapsulant"),
            backsheet=mo.ui.text(label="Backsheet"),
            frame_material=mo.ui.text(label="Frame Material"),
            x=mo.ui.number(label="X Position", step=1),
            y=mo.ui.number(label="Y Position", step=1),
        )
        .form(label="Submit Module Metadata", show_clear_button=True)
    )
    return (form,)


@app.cell
def _(form):
    form
    return


@app.cell
def _(form):
    print(form.value)
    return


@app.cell
def _(Table, engine, metadata, pg_insert):
    def insert_module_metadata(data: dict):
        module_table = Table("module_metadata", metadata, autoload_with=engine, schema="instrument_data")
        stmt = pg_insert(module_table).values(data).on_conflict_do_nothing(index_elements=["module_id"])
        with engine.begin() as conn:
            conn.execute(stmt)
    return (insert_module_metadata,)


@app.cell
def _(form, insert_module_metadata, mo):
    if form.value is not None:
        insert_module_metadata(form.value)
        mo.md("✅ Submitted to PostgreSQL!").callout(kind="success")
    return


@app.cell
def _(engine, instrument_data, mo, module_metadata):
    modules_df = mo.sql(
        f"""
        SELECT * FROM instrument_data.module_metadata
        """,
        output=False,
        engine=engine
    )
    return (modules_df,)


@app.cell
def _(mo, modules_df):
    mo.ui.dataframe(modules_df)
    return


if __name__ == "__main__":
    app.run()
