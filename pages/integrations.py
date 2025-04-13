from shiny import ui

def layout():
    return ui.page_fluid(
        ui.h3("Integrations"),
        ui.p("This page can be used to embed dashboards, graphs, or external services."),
        ui.tags.iframe(src="https://example.com", height="400", width="100%")
    )

def server(input, output, session):
    pass