"""
03-bathy-voice.py — Use the Voice opener on the bathy chart.

The Voice opener reads the bathy chart aloud. Each cell becomes a phrase.
The sailor (or a blind sailor) can hear the bottom of the sea.

Fable 06 (Grandmother): the opener should be usable by anyone, even
a 91-year-old. The voice opener uses plain language, no jargon.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from bathy import BathyChart, Sailor, ConvoyBoat
from quilt_substrate.openers import VoiceOpener


def main():
    chart = BathyChart()
    for i in range(5):
        boat = ConvoyBoat(name=f"boat-{i:02d}")
        for x, y, d in boat.survey(n=5):
            chart.add_convoy_sounding(x, y, d, agent=boat.name)
    reyes = Sailor(name="reyes")
    for x, y, d in reyes.survey(n=20):
        chart.add_sounding(x, y, d, agent=reyes.name)
    print(f"Chart: {len(chart.substrate)} cells")
    print()
    print("Voice opener (TTS-friendly):")
    for event in VoiceOpener().activate(chart.substrate):
        print(f"  {event['text']}")


if __name__ == "__main__":
    main()
