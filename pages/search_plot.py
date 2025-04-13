from shiny import ui, render, reactive
from db import query_data
import matplotlib.pyplot as plt

def layout():
    return ui.page_fluid(
        ui.h3("Search & Plot"),
        ui.input_text("filter", "Filter by Category", placeholder="Leave empty for all"),
        ui.input_action_button("search", "Search"),
        ui.output_data_frame("table"),
        ui.output_plot("plot")
    )

def server(input, output, session):
    data = reactive.value(None)

    @reactive.effect
    @reactive.event(input.search)
    def _():
        df = query_data(input.filter() or None)
        data.set(df)

    @output
    @render.data_frame
    def table():
        return data() if data() is not None else []

    @output
    @render.plot
    def plot():
        df = data()
        if df is not None and not df.empty:
            plt.clf()
            df.groupby("category")["value"].sum().plot(kind="bar")
            plt.ylabel("Sum of Values")