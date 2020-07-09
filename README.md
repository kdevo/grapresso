<a href="https://git.io/grapresso" target="_blank">
    <img alt="Grapresso Logo" src="https://raw.githubusercontent.com/kdevo/grapresso/master/.github/logo.png" width="512" width="64">
</a>
<a href="https://travis-ci.org/kdevo/grapresso" target="_blank">
    <img align="right" alt="Travis CI Build Status" src="https://travis-ci.org/kdevo/grapresso.svg?branch=master">
</a>

---

Caffeinated Python graph data structure library originated from an academical context (see [Development](#Development)).
 
**Grapresso** :coffee: is like a good espresso among other common graph libraries:

- **Quickly consumed**: Easy-to-learn and setup - [just try it](#Usage)!
- **Different flavours**: Choose your [backend](#Backends)
- **Beans are first class**: Object-oriented approach with nodes as first [*class citizens*](https://github.com/kdevo/grapresso/blob/master/grapresso/components/node.py#L7)
- **Concentrated**: [Clear and concise *algorithms*](https://github.com/kdevo/grapresso/blob/master/grapresso/components/graph.py#L117)
- **Make your Macchiato**: Extensible by design, e.g. [proven by the new NetworkX backend implementation](#Implementations)
- **Well tested ingredients**: Stress-[integration-tested](https://github.com/kdevo/grapresso-it) using *huge* graphs
- **Clean and lightweight**: Written in pure *Python 3*, 
[no other libraries needed](https://github.com/kdevo/grapresso/blob/master/setup.py#L25) 

Grapresso works wonderfully with PyPy and is up to [up to 4x faster than your regular Python](https://travis-ci.org/github/kdevo/grapresso/builds/704782062) :cake: :zap:
 

> There are many popular algorithms that are **not** yet implemented.
Feel free to contribute! Make it feel like home for your own graph algorithms if you want to.
>
> :bulb: Since July 2020, you can also use Grapresso as a middleman for NetworkX thanks to the NetworkX backend.
> Therewith, you can utilize the full power of NetworkX in case an algorithm is not implemented in Grapresso.
 
## Usage

Want to get the shortest tour (round-trip) for [TSP](https://en.wikipedia.org/wiki/Travelling_salesman_problem)? Usage is easy:

```python
from grapresso import Graph

# Build a fully connected graph using InMemoryBackend (default if no backend is given):
graph = Graph() \
    .add_edge("Aachen", "Amsterdam", cost=230) \
    .add_edge("Amsterdam", "Brussels", cost=200) \
    .add_edge("Brussels", "Aachen", cost=142)

# Now also add Luxembourg - note that every city needs to be connected to it for the graph to stay fully connected:
for city, dist in zip(("Aachen", "Brussels", "Amsterdam"), (200, 212, 420)):
    graph.add_edge(city, "Luxembourg", dist)

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

> :warning: Be careful, the `PickleFileBackend` is not properly tested and more of an experiment right now!

## Development

This project has been created in the subject "Mathematical Methods for Computer Science" (translated from the German "Mathematische Methoden der Informatik")  at the FH Aachen.
Contributions are welcome!

### Conventions
- :deciduous_tree: [Project structure](https://docs.python-guide.org/writing/structure/)
- :beers: [gitmoji](https://gitmoji.carloscuesta.me/) - Semantic commit messages