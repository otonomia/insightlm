import os
import platform
import subprocess
import time
from pathlib import Path

import pyautogui
import pytesseract
from openai import OpenAI


class CalculatorAgent:
    """A tiny agent that explores the system calculator and writes a user guide.

    The implementation uses ``pyautogui`` for UI automation, ``pytesseract`` to
    read the calculator display via OCR and the OpenAI API to turn the recorded
    observations into documentation.
    """

    def __init__(self) -> None:
        self.client = OpenAI()  # requires ``OPENAI_API_KEY`` environment variable
        self.logs: list[str] = []

    # -- UI helpers -----------------------------------------------------
    def launch(self) -> None:
        """Launch the OS calculator application."""
        system = platform.system()
        if system == "Windows":
            subprocess.Popen("calc.exe")
        elif system == "Darwin":
            subprocess.Popen(["open", "-a", "Calculator"])
        else:
            subprocess.Popen(["gnome-calculator"])  # Linux
        time.sleep(1)  # give the window time to appear

    def press(self, keys: list[str]) -> None:
        """Press a sequence of keys on the keyboard."""
        for key in keys:
            pyautogui.press(key)
            time.sleep(0.2)

    def read_display(self) -> str:
        """Capture the calculator display via screenshot and OCR."""
        screenshot = pyautogui.screenshot()
        text = pytesseract.image_to_string(screenshot)
        return text.strip()

    # -- Agent workflow -------------------------------------------------
    def explore(self) -> None:
        """Perform a small number of operations to learn about the app."""
        self.press(["2", "+", "2", "enter"])
        result = self.read_display()
        self.logs.append(f"Pressed 2+2 => {result}")

        self.press(["escape"])
        self.press(["5", "*", "3", "enter"])
        result = self.read_display()
        self.logs.append(f"Pressed 5*3 => {result}")

    def generate_documentation(self, path: Path = Path("Calculator_User_Guide.md")) -> None:
        """Turn the collected logs into a short user guide."""
        prompt = (
            "You are a technical writer. Using the interaction logs below, "
            "write a concise Markdown user guide for a basic calculator.\n\n"
            f"Logs:\n{os.linesep.join(self.logs)}"
        )
        response = self.client.responses.create(
            model="gpt-4o-mini",
            input=prompt,
        )
        path.write_text(response.output_text, encoding="utf-8")


def main() -> None:
    agent = CalculatorAgent()
    agent.launch()
    agent.explore()
    agent.generate_documentation()


if __name__ == "__main__":
    main()
