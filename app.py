from shiny import App, ui
from pages import add_data, search_plot, integrations
from db import create_table

create_table()

app_ui = ui.page_navbar(
    ui.nav_panel("Add Data", add_data.layout()),
    ui.nav_panel("Search & Plot", search_plot.layout()),
    ui.nav_panel("Integrations", integrations.layout()),
    title="Shiny SQLite App"
)

def server(input, output, session):
    add_data.server(input, output, session)
    search_plot.server(input, output, session)
    integrations.server(input, output, session)

app = App(app_ui, server)