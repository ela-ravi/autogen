from typing import Callable

# Step weights mapping step number to (start_pct, end_pct)
STEP_WEIGHTS = {
    1: (0, 20),     # Transcription
    2: (20, 25),    # Translation
    3: (25, 40),    # Recap generation
    4: (40, 65),    # Clip extraction
    5: (65, 70),    # Audio removal
    6: (70, 85),    # TTS generation
    7: (85, 100),   # Audio-video merge
}

STEP_NAMES = {
    1: "Transcribing video",
    2: "Translating transcription",
    3: "Generating recap suggestions",
    4: "Extracting and merging clips",
    5: "Removing original audio",
    6: "Generating TTS narration",
    7: "Merging audio with video",
}


class ProgressReporter:
    """Converts per-step progress into overall job progress."""

    def __init__(self, on_progress: Callable):
        """
        on_progress: called with (step, step_name, progress_pct, message)
        """
        self.on_progress = on_progress

    def report(self, step: int, message: str, sub_progress: float = 1.0):
        """Report progress for a step.

        Args:
            step: Step number (1-7)
            message: Human-readable message
            sub_progress: Progress within this step (0.0 to 1.0)
        """
        start, end = STEP_WEIGHTS.get(step, (0, 100))
        overall_pct = start + (end - start) * sub_progress
        step_name = STEP_NAMES.get(step, f"Step {step}")

        self.on_progress(
            step=step,
            step_name=step_name,
            progress_pct=round(overall_pct, 1),
            message=message,
        )

    def step_callback(self, step: int, message: str):
        """Simple callback for adapters — reports step as started."""
        self.report(step, message, sub_progress=0.5)
