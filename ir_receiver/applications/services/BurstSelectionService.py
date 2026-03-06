class BurstSelectionService:
    def select(self, captured: list[list[int]], selected_index: int = 0) -> list[int]:
        if not captured:
            return []

        if selected_index < 0 or selected_index >= len(captured):
            return captured[0]

        return captured[selected_index]
