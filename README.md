# Priorean Temporal Logic and Minkowski Spacetime Checker

This repository contains two Python programs, `real-time.py` and `minkowski-spacetime.py`, designed for checking satisfiability of Priorean temporal logic formulas over the real line and in the irreflexive 2-dimensional Minkowski spacetime, respectively.

## `real-time.py`

### Overview
The `real-time.py` program implements a filtration procedure for Priorean temporal logic. It is designed to check the validity of Priorean temporal formulas over the real line with the usual order. If the formula is satisfiable, the program outputs a possible filtration model, which consists of an alternating sequence of clusters and maximal consistent sets.

### Formula Syntax
- **Operators:** The program supports Priorean temporal operators: F, P, H, and G, all in uppercase.
- **Propositional Logic:** Use the following symbols for logical operations: `~` for NOT, `|` for OR, `&` for AND, and `>` for IMPLIES.
- **Atomic Formulas:** Atomic formulas are represented by lowercase letters.
- **Conjunctions:** Ensure that conjunctions, e.g., `(p&q)` or `(Fp|Gp)`, are enclosed in brackets.

### Usage
To run the program, simply execute the `real-time.py` file. It will prompt you to enter a Priorean temporal formula:

```shell
$ python real-time.py
Enter a temporal formula:
```

## `minkowski-spacetime.py`

### Overview
The `minkowski-spacetime.py` program implements an algorithm to check the satisfiability of formulas in the irreflexive Minkowski spacetime.

### Formula Syntax
- **Operators:** The program supports Priorean temporal operators: F, P, H, and G, all in uppercase.
- **Propositional Logic:** Use the following symbols for logical operations: `~` for NOT, `|` for OR, `&` for AND, and `>` for IMPLIES.
- **Atomic Formulas:** Atomic formulas are represented by lowercase letters.
- **Conjunctions:** Ensure that conjunctions, e.g., `(p&q)` or `(Fp|Gp)`, are enclosed in brackets.

### Usage
To run the program, simply execute the `minkowski-spacetime.py` file. It will prompt you to enter a formula for the irreflexive 2-dimensional Minkowski spacetime:

```shell
$ python minkowski-spacetime.py
Enter a temporal formula:
```

### Note
The algorithm in `minkowski-spacetime.py` is sound but not complete. It will always correctly determine when a formula is not satisfiable. To guarantee satisfiability, additional checks must be carried out. 
