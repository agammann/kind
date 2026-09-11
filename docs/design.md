# Design reference

The primary-screen concept was generated using the built-in image-generation tool. A reference copy is retained with the local deliverables as `docs/design-concept.png` (excluded from Git); it is not a product screenshot and is not used as the UI.

Prompt: A complete readable desktop screen for Kind, a nonprofit shift coordinator. White background, cobalt blue #234BD8, ink #172647, gray #F4F6FA, green success and amber warnings. Left sidebar with Kind, Coverage, Volunteers and Activity. Main heading Every shift matters. Three real-state counts. Upcoming shift list, selected shift details, right recommendation panel with eligibility checks, invitation review controls and a clear human-approval note. Sample Riverbend Food Bank records. No marketing hero, decorative artwork, or invented analytics.

Implementation preserves the layout, palette, and hierarchy while replacing generated counts and incidental text with actual application state. The code adds necessary error, approval, decline, and response views. Small screens stack the working panels and expose the navigation across the top.
