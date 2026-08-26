# quilt-bathy

> *The bathy cross-section as a working tool. The substrate, applied to the sailor's actual use case. The Inner Sound, as a cell-graph.*

## What is this?

A sailor on a small fishing boat has a 12-inch tablet with a chart. The chart shows the bottom of the ocean. The chart is *backed by the substrate* — every cell is a depth, every cell has a tensor, every cell has a confidence, every cell has a witness log.

The chart shows:
- The **depths** the sailor has personally surveyed (high confidence, no decay)
- The **convoy's inferred depths** (lower confidence, slow decay)
- The **fog-of-war** — cells that have not been refreshed in 30 days are darker
- The **tack cross-section** — a slice through the substrate along the sailor's intended tack

This tool implements the bathy cross-section (scenario 03) as a *working* application of the substrate. It is not a demo. It is a tool the sailor can use on the boat.

## Install

```bash
pip install quilt-bathy
```

Or from source:

```bash
git clone https://github.com/SuperInstance/quilt-bathy
cd quilt-bathy
pip install -e .
```

This requires `quilt-substrate` to be installed.

## Quick start

```python
from quilt_bathy import BathyChart, ConvoyBoat, Sailor

# Create a small bay
chart = BathyChart(bounds={"x": (0, 100), "y": (0, 100), "depth": (0, 30)})

# Add the convoy: 10 boats, each writing their soundings
for i in range(10):
    boat = ConvoyBoat(name=f"boat-{i:02d}")
    for x, y, d in boat.survey():
        chart.add_sounding(x, y, d, agent=boat.name)

# Add the sailor: Reyes, with her own soundings
reyes = Sailor(name="reyes")
for x, y, d in reyes.survey():
    chart.add_sounding(x, y, d, agent=reyes.name)

# Render the cross-section along a planned tack
cross_section = chart.cross_section(start=(10, 50), end=(90, 50))
for point in cross_section:
    print(f"  x={point['x']}, y={point['y']}, depth={point['depth']:.2f}, confidence={point['confidence']:.3f}")
```

The full example is in `examples/01-the-inner-sound.py`.

## The chart

The chart is a `BathyChart`, which is a thin wrapper around a `quilt-substrate` `Substrate`. Each cell in the substrate is a depth measurement at a particular (x, y) coordinate. The cell's tensor is `(depth,)`. The cell's value is the current depth. The cell's confidence is the decay-weighted freshness. The cell's witness log records every agent (boat) that has read or written the depth.

The chart supports:

- `add_sounding(x, y, depth, agent)` — add a single sounding
- `cross_section(start, end)` — render a cross-section along a line
- `fog_of_war()` — show cells that have not been refreshed
- `convoy_view()` — show the convoy's coverage map
- `render_ascii()` — render the chart as ASCII (for the terminal, for the satellite link)

## The sailor

The sailor is the *user* of the substrate. The sailor has her own high-resolution data. The sailor's data is canonical. The convoy's data is inferred. The substrate's confidence is the *honesty* of the inference.

The sailor's actions:

- `s.add_sounding(x, y, depth, agent=reyes)` — a fresh sounding, high confidence
- `chart.refresh(x, y)` — refresh a cell, reset the decay clock
- `chart.cross_section(...)` — render a view
- `chart.fog_of_war()` — see where the substrate is stale

## The convoy

The convoy is the *fleet* of boats. Each boat is an agent. Each boat writes soundings. The convoy is the *substrate's witness log*.

The convoy's actions:

- `boat.survey()` — return a list of soundings
- `chart.add_convoy_sounding(x, y, depth, agent=boat.name)` — add a convoy sounding

## The cross-section

The cross-section is the sailor's *control surface*. The cross-section is not a view; it is a *plan*. The cross-section tells the sailor where she can go and where she cannot. The cross-section is the substrate's most important opener.

The cross-section is rendered as a list of `(x, y, depth, confidence)` points. The sailor uses the cross-section to plan her next tack.

## The fog of war

The fog of war is the substrate's *honesty about its own limits*. Cells that have not been refreshed in 30 days are dark. The sailor knows where her data is fresh and where the convoy's data is stale. The fog of war is the substrate's *honest* answer to "where do you not know?"

## The test suite

- `test_chart.py` — the BathyChart wrapper
- `test_sailor.py` — the Sailor class
- `test_convoy.py` — the ConvoyBoat class
- `test_cross_section.py` — the cross-section rendering
- `test_fog_of_war.py` — the fog-of-war decay
- `test_fable_03.py` — fable 03 (The Convoy) as integration test
- `test_fable_02.py` — fable 02 (The Sailor's Tablet) as integration test

## The fables

- **Fable 02 (The Sailor's Tablet)** — *The chart is a language, not a map.* The chart speaks in metaphor where the substrate would speak in numbers.
- **Fable 03 (The Convoy)** — *100 boats writing to the same cell-graph. The convoy is the agent.*
- **Fable 11 (The Paper and the Tablet)** — *A picture is honest by staying silent. A conversation is honest by speaking its uncertainty out loud.*
- **Fable 23 (The Flute and the Murmur)** — *The chart's depth is one note. The convoy's murmur is many notes.*

## License

MIT.

---

*— Mavis, 24 August 2026*
*Built from the seed canon, paper 107-116, and the user's "take everything as far as your team is able" instruction. The substrate is the soil. The bathy is the plant. The sailor is the gardener.*


---

## Roaming the Quilt collection

You came through the **bathy:0**. That's one of twenty-four doors
into the same idea — the 5-opcode polyformalism. The other doors are
metaphored for different audiences (mathematicians, hardware hackers,
web developers, hardware folks, story readers), but the substrate is
the same.

**The full map of the collection:** [COLLECTION.md](https://github.com/SuperInstance/AI-Writings/blob/master/seed-canon/COLLECTION.md)

**From here, three wander-paths you might enjoy:**

1. **[quilt-foundation](https://github.com/SuperInstance/quilt-foundation)** — the foundational doc that ties the 5 opcodes together
2. **[quilt-substrate](https://github.com/SuperInstance/quilt-substrate)** — the original Python substrate that bathy:0 runs on
3. **[quilt-ecosystem-demo](https://github.com/SuperInstance/quilt-ecosystem-demo)** — the 12-inch tablet demo that uses bathy:0

The cowboy's maxim: *The unit of foundation is the cell, not the
opcode. The 5 opcodes are the 5 messages a cell can receive. The 24
repos are the 24 doors into the same message. The cowboy is the one
who wanders.*
