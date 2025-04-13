from shiny import ui, render, reactive
from db import insert_data

def layout():
    return ui.page_fluid(
        ui.h3("Add New Data"),
        ui.input_text("name", "Name"),
        ui.input_numeric("value", "Value", value=0),
        ui.input_text("category", "Category"),
        ui.input_action_button("submit", "Add to Database"),
        ui.output_text("result")
    )

def server(input, output, session):
    @reactive.effect
    @reactive.event(input.submit)
    def _():
        insert_data(input.name(), input.value(), input.category())
        output.result.set_text("Data added successfully!")