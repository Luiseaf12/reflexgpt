import reflex as rx
from fullstackgpt import ui, navigation


def home_page() -> rx.Component:
    # Welcome Page (Index)
    return ui.base_layout(
        rx.vstack(
            rx.heading("Welcome to Reflex!", size="5"),
            spacing="5",
            justify="center",
            min_height="85vh",
        ),
        rx.logo(),
    )
