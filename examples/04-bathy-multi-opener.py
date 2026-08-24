"""
04-bathy-multi-opener.py — Use the new openers on the bathy chart.

Demonstrates the Opener ABC's extensibility: a single bathy chart
can be rendered as a chart, voice (TTS), gesture (touch), MIDI
(music), REST (API), MUD (text adventure), and PLATO (lesson).

Fable 10 (Conductor): the substrate is an orchestra. The MIDI opener
turns the bay into a symphony of depths.
Fable 06 (Grandmother): the PLATO opener turns the bay into a lesson.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from bathy import BathyChart, Sailor, ConvoyBoat
from quilt_substrate.openers import (
    ChartOpener, VoiceOpener, GestureOpener, MIDIOpener,
    RESTOpener, MUDOpener, PLATOOpener,
)


def main():
    chart = BathyChart()
    for i in range(3):
        boat = ConvoyBoat(name=f"boat-{i:02d}")
        for x, y, d in boat.survey(n=5):
            chart.add_convoy_sounding(x, y, d, agent=boat.name)
    reyes = Sailor(name="reyes")
    for x, y, d in reyes.survey(n=15):
        chart.add_sounding(x, y, d, agent=reyes.name)
    print(f"Chart: {len(chart.substrate)} cells\n")

    # Chart
    print("=== Chart (data view) ===")
    for e in ChartOpener().activate(chart.substrate):
        if e["kind"] == "value":
            print(f"  {e['address']}: {e['value']} (conf={e['confidence']:.2f})")

    # Voice
    print("\n=== Voice (TTS) ===")
    for e in list(VoiceOpener().activate(chart.substrate))[:3]:
        print(f"  {e['text']}")

    # MIDI
    print("\n=== MIDI (symphony of depths) ===")
    notes = list(MIDIOpener().activate(chart.substrate))
    if notes:
        # Show a 4-bar melody
        for e in notes[:4]:
            print(f"  Note {e['note']:3d}, velocity {e['velocity']:3d}, channel {e['channel']}")

    # MUD
    print("\n=== MUD (text adventure) ===")
    for e in list(MUDOpener().activate(chart.substrate))[:2]:
        print(f"  {e['description']}")
        if e['exits']:
            print(f"    Exits: {e['exits']}")

    # PLATO
    print("\n=== PLATO (lesson) ===")
    for e in list(PLATOOpener().activate(chart.substrate))[:2]:
        print(f"  Title: {e['title']}")
        print(f"  Content: {e['content']}")

    # REST
    print("\n=== REST (API) ===")
    for e in list(RESTOpener().activate(chart.substrate))[:2]:
        print(f"  {e['method']} {e['path']}")


if __name__ == "__main__":
    main()
