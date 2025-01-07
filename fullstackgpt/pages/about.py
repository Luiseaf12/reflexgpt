import reflex as rx
from fullstackgpt import ui


def about_page() -> rx.Component:
    # Welcome Page (Index)
    return ui.base_layout(
        rx.color_mode.button(position="top-left"),
        rx.vstack(
            rx.heading("About Us", size="9"),
            rx.text(
                "about ",
                size="5",
            ),
            rx.link(
                rx.button("inicio"),
                href="/",
            ),
            spacing="5",
            justify="center",
            min_height="85vh",
        ),
        rx.logo(),
    )
