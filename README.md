# Quantum Actor System

A beautiful implementation of a quantum particle system using actor-based processing and topological quantum computation concepts.

## Features

- Actor-based quantum processing
- Differential form computations
- Knot theory integration
- Asynchronous evolution
- Topological constraints

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the System

Simply run:
```bash
python src/quantum_system.py
```

The system will simulate 10 quantum particles evolving through 100 timesteps, displaying energy and writhe number at each step.

## Architecture

The system uses an actor-based architecture with:
- QuantumActor: Base class for all quantum processing units
- DifferentialProcessor: Handles quantum differential forms
- KnotProcessor: Computes topological invariants
- QuantumSystem: Main orchestrator

Each component communicates asynchronously through message passing, allowing for natural quantum parallelism. 