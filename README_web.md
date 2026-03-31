# Web interface

This repository now includes a Streamlit-based web interface in `app.py`.

## Features

- Compute closure of an attribute set
- Compute all closures
- Compute candidate keys
- Find prime attributes
- Compute a minimal cover
- Project dependencies onto a sub-relation
- Discover functional dependencies from a CSV table
- Generate random FD instances

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Input format for functional dependencies

Enter one dependency per line:

```text
A -> B
A,B -> C,D
B,C -> A
```

## Relation input for discovery

Either upload a CSV file or paste a Python dictionary such as:

```python
{
    'A': [1, 1, 2, 2],
    'B': [5, 5, 6, 7],
    'C': [9, 9, 9, 10]
}
```
