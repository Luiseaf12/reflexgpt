import reflex as rx
from fullstackgpt import ui
from datetime import datetime


def pricing_page() -> rx.Component:
    # Get current year
    current_year = datetime.now().year
    years = [str(year) for year in range(2020, current_year + 1)]
    
    return ui.base_layout(
        rx.color_mode.button(position="top-left"),
        rx.vstack(
            rx.heading("Precios", size="9"),
            rx.select(
                years,
                value="2025",
                placeholder="Seleccione un año",
            ),

            spacing="5",
            justify="center",
            min_height="85vh",
        ),
        rx.logo(),
    )
