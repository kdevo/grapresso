<a href="https://git.io/grapresso" target="_blank">
    <img alt="Grapresso Logo" src="https://raw.githubusercontent.com/kdevo/grapresso/master/.github/logo.png" width="512" width="64">
</a>
<a href="https://travis-ci.org/kdevo/grapresso" target="_blank">
    <img align="right" alt="Travis CI Build Status" src="https://travis-ci.org/kdevo/grapresso.svg?branch=master">
</a>

---

Caffeinated Python graph data structure library originated from an academical context (see [Development](#Development)).
 
**Grapresso** :coffee: is like a good espresso among other common graph libraries:

- **Quickly consumed**: Easy-to-learn and setup
- **Selectable flavours**: Choose your purpose-dependent *storage format* (e.g. in-memory or file-based)
- **Beans are first class**: The graph nodes are the first class citizens, not the edges
- **Clean and lightweight**: Written in pure *Python 3*, no external libraries needed
- **Concentrated**: Clear and concise *algorithms*
- **Make your Macchiato**: Extensible by design
- **Well tested ingredients**: Stress-[integration-tested](https://github.com/kdevo/grapresso-it) using *huge* graphs

> There are many popular algorithms that are **not** yet implemented.
Feel free to contribute! Make it feel like home for your own graph algorithms if you want to.

## Usage

Want to get the shortest tour (round-trip) for [TSP](https://en.wikipedia.org/wiki/Travelling_salesman_problem)? Usage is easy:

```python
from grapresso import BiGraph

# Build a fully connected graph using InMemoryBackend (default if no backend is given):
graph = BiGraph() \
    .add_edge("Aachen", "Amsterdam", cost=230) \
    .add_edge("Amsterdam", "Brussels", cost=200) \
    .add_edge("Brussels", "Aachen", cost=142)

# Now also add Luxembourg - note that every city needs to be connected to it for the graph to stay fully connected:
for city, dist in zip(("Aachen", "Brussels", "Amsterdam"), (200, 212, 420)):
    graph.add_edge(city, "Luxembourg", cost=dist)

tour = graph.cheapest_tour("Aachen")
assert tour.cost == 842
print(tour)
```

See [tests directory](tests) for more examples!

## Architecture

Grapresso provides a clean API so that you can easily extend it to store the graph's structure in your preferred storage format.
Algorithms are implemented completely independent from the backend.

### Backends
Algorithms are performed on a so called "backend" which wraps the graph's internal data structure.

The API is defined in [backend/api.py](grapresso/backend/api.py). Therewith, backends can easily be added provided that they carefully implement the defined API.

#### Implementations
Implementation                                           | Type                                                  | Underlying data structure                   
-------------------------------------------------------- | ----------------------------------------------------- | -------------------------------
[InMemoryBackend](/grapresso/backend/memory.py)          | In-Memory with Traits                                 | `{node_name: obj}` 
[NetworkXBackend](/grapresso/backend/networkx.py)        | [NetworkX](https://networkx.github.io/) compatible    | nx.DiGraph with custom NetworkXNodes
[PickleFileBackend](/grapresso/backend/file.py)          | Pickle file-based                                     | Files with `${hash(obj)}.node` as filename

> :warning: Be careful, the `PickleFileBackend` is not properly tested and more of an experiment right now!

## Development

This project has been created in the subject "Mathematical Methods for Computer Science" (translated from the German "Mathematische Methoden der Informatik")  at the FH Aachen.
Contributions are welcome!

### Conventions
- :deciduous_tree: [Project structure](https://docs.python-guide.org/writing/structure/)
- :beers: [gitmoji](https://gitmoji.carloscuesta.me/) - Semantic commit messages