"""
02-trainer-on-bathy.py — Substrate-trainer applied to the bathy chart.

A small example showing how to:
1. Build a bathy chart with a convoy
2. Take its witness log
3. Train a JEPA-like model
4. Predict the depth at un-surveyed locations
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "quilt-substrate", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "substrate-trainer", "src"))
from bathy import BathyChart, Sailor, ConvoyBoat
from trainer import Trainer


def main():
    # Build the chart
    chart = BathyChart()
    for i in range(20):
        boat = ConvoyBoat(name=f"boat-{i:02d}")
        for x, y, d in boat.survey(n=10):
            chart.add_convoy_sounding(x, y, d, agent=boat.name)
    reyes = Sailor(name="reyes")
    for x, y, d in reyes.survey(n=80):
        chart.add_sounding(x, y, d, agent=reyes.name)
    print(f"Chart: {len(chart.substrate)} cells")

    # Train a JEPA-like model on the substrate's witness log
    trainer = Trainer()
    model = trainer.fit(chart.substrate, n_epochs=30)
    print(f"Trained: {model.n_train} examples, {len(model.agent_to_id)} agents")

    # Predict: what would the model guess for an un-surveyed context?
    print()
    print("Predictions:")
    for ctx in [["reyes"], ["reyes", "boat-00"], ["boat-00", "boat-01"]]:
        pred, conf = model.predict(ctx)
        print(f"  Predict({ctx}): depth={pred:.2f}m, model_confidence={conf:.2f}")

    # Show that the model learned the substrate's pattern
    print()
    print("The model learned from the witness log. The substrate is the soil.")
    print("The bathy is the plant. The trainer is the gardener.")


if __name__ == "__main__":
    main()
