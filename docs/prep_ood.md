# Object-Oriented Design: SOLID Principles & Design Patterns

## Overview

Object-oriented design (OOD) is a foundational interview topic for MLE and software engineering roles. Interviewers test your ability to decompose systems into well-structured classes with clear responsibilities and relationships. This document covers the SOLID principles that guide class design, four essential design patterns (Observer, Composite, State, Singleton), and a systematic approach to OOD interview problems like elevator systems and parking lots.

## Core Concepts

### SOLID Principles

SOLID is a mnemonic for five design principles that produce maintainable, extensible code:

| Principle | Full Name | One-Line Rule |
|-----------|-----------|---------------|
| **S** | Single Responsibility | A class should have only one reason to change |
| **O** | Open-Closed | Open for extension, closed for modification |
| **L** | Liskov Substitution | Subtypes must be substitutable for their base types |
| **I** | Interface Segregation | Prefer specific interfaces over fat universal ones |
| **D** | Dependency Inversion | Depend on abstractions, not concrete implementations |

### Single Responsibility Principle (SRP)

A class should have **exactly one reason to change** -- meaning it encapsulates exactly one responsibility. When a class handles multiple concerns, changes to one concern risk breaking another.

```python
# Violation: User handles both data AND notification
class User:
    def save(self) -> None: ...
    def send_email(self, msg: str) -> None: ...

# Fixed: separate responsibilities
class User:
    def save(self) -> None: ...

class UserNotifier:
    def send_email(self, user: User, msg: str) -> None: ...
```

**Interview signal**: If you can describe a class's purpose with "and" (e.g., "manages users *and* sends notifications"), it likely violates SRP.

### Open-Closed Principle (OCP)

Software entities should be **open for extension** but **closed for modification**. Add new behavior by adding new code (subclasses, strategy objects), not by editing existing code.

```python
from abc import ABC, abstractmethod

class PricingStrategy(ABC):
    @abstractmethod
    def calculate(self, base_price: float) -> float: ...

class RegularPricing(PricingStrategy):
    def calculate(self, base_price: float) -> float:
        return base_price

class DiscountPricing(PricingStrategy):
    def calculate(self, base_price: float) -> float:
        return base_price * 0.9

# Adding a new pricing type requires NO changes to existing classes
class PremiumPricing(PricingStrategy):
    def calculate(self, base_price: float) -> float:
        return base_price * 1.2
```

**Key mechanism**: The Strategy pattern is the canonical OCP implementation -- define behavior as pluggable objects rather than conditional branches.

### Liskov Substitution Principle (LSP)

If $S$ is a subtype of $T$, then objects of type $T$ may be replaced with objects of type $S$ without altering correctness. The classic violation:

```python
class Rectangle:
    def __init__(self, w: float, h: float) -> None:
        self.width = w
        self.height = h

    def area(self) -> float:
        return self.width * self.height

class Square(Rectangle):
    def __init__(self, side: float) -> None:
        super().__init__(side, side)
    # Problem: setting width independently breaks the square invariant
    # A Square cannot substitute for Rectangle if callers expect
    # independent width/height assignment
```

**LSP test**: Can you pass the subclass everywhere the superclass is expected without surprising behavior? If not, the inheritance relationship is wrong -- consider composition instead.

### Interface Segregation Principle (ISP)

Clients should not be forced to depend on interfaces they do not use. Split fat interfaces into focused ones:

```python
from abc import ABC, abstractmethod

# Violation: forces all workers to implement eat()
class IWorker(ABC):
    @abstractmethod
    def work(self) -> None: ...
    @abstractmethod
    def eat(self) -> None: ...

# Fixed: separate interfaces
class IWorkable(ABC):
    @abstractmethod
    def work(self) -> None: ...

class IFeedable(ABC):
    @abstractmethod
    def eat(self) -> None: ...

class HumanWorker(IWorkable, IFeedable):
    def work(self) -> None: ...
    def eat(self) -> None: ...

class RobotWorker(IWorkable):
    def work(self) -> None: ...
    # No need to implement eat()
```

**Python note**: Python uses ABCs and duck typing rather than explicit interfaces. ISP still applies -- keep ABCs small and focused.

### Dependency Inversion Principle (DIP)

High-level modules should not depend on low-level modules. Both should depend on abstractions.

```python
from abc import ABC, abstractmethod

class Database(ABC):
    @abstractmethod
    def query(self, sql: str) -> list: ...

class PostgresDB(Database):
    def query(self, sql: str) -> list:
        # Postgres-specific implementation
        return []

class UserRepository:
    def __init__(self, db: Database) -> None:  # depends on abstraction
        self._db = db

    def find_user(self, user_id: int) -> dict:
        return self._db.query(f"SELECT * FROM users WHERE id={user_id}")[0]
```

**Why it matters**: DIP enables testability (inject mock DB), swappability (switch to MySQL), and decoupling (high-level logic is unaware of storage details).

### Observer Pattern

A **subject** maintains a list of **observers** and notifies them of state changes. Used for event-driven systems where publishers and subscribers are decoupled.

```python
from abc import ABC, abstractmethod

class Observer(ABC):
    @abstractmethod
    def update(self, data: dict) -> None: ...

class Subject:
    def __init__(self) -> None:
        self._observers: list[Observer] = []

    def attach(self, obs: Observer) -> None:
        self._observers.append(obs)

    def detach(self, obs: Observer) -> None:
        self._observers.remove(obs)

    def notify(self, data: dict) -> None:
        for obs in self._observers:
            obs.update(data)
```

Key responsibilities:
- **Subject**: Maintain observer list, notify on state change via `update()`
- **Observer**: Register/unregister on subject, synchronize state when notified

**Observer vs Pub/Sub**: Observer is direct (subject knows observers). Pub/Sub introduces a message broker -- publishers and subscribers are fully decoupled and unaware of each other. Pub/Sub scales better in distributed systems; Observer is simpler for in-process notifications.

### Composite Pattern

Represents **part-whole hierarchies** as tree structures so clients treat individual objects and compositions uniformly.

```python
from abc import ABC, abstractmethod

class Component(ABC):
    @abstractmethod
    def operation(self) -> str: ...

class Leaf(Component):
    def __init__(self, name: str) -> None:
        self.name = name

    def operation(self) -> str:
        return self.name

class Composite(Component):
    def __init__(self) -> None:
        self._children: list[Component] = []

    def add(self, child: Component) -> None:
        self._children.append(child)

    def operation(self) -> str:
        results = [c.operation() for c in self._children]
        return f"Branch({'+'.join(results)})"
```

Key properties:
- Unified `Component` interface for both leaves and branches
- Requests propagate down the tree (forwarded to children)
- Client code treats leaf and composite objects identically

**Use cases**: File systems (files vs directories), UI widget trees, organization charts.

### State Pattern

Allows an object to **alter its behavior when its internal state changes**, appearing to change its class at runtime. Eliminates complex conditional logic.

```python
from abc import ABC, abstractmethod

class State(ABC):
    @abstractmethod
    def handle(self, context: "Context") -> None: ...

class IdleState(State):
    def handle(self, context: "Context") -> None:
        print("Starting work...")
        context.state = WorkingState()

class WorkingState(State):
    def handle(self, context: "Context") -> None:
        print("Work complete, going idle.")
        context.state = IdleState()

class Context:
    def __init__(self) -> None:
        self.state: State = IdleState()

    def request(self) -> None:
        self.state.handle(self)
```

Key properties:
- State-specific behavior is defined independently in state classes
- Adding new states does not affect existing states (OCP)
- The context delegates behavior to the current state object

**State vs Strategy**: Both use composition. State transitions are implicit (the state object decides the next state). Strategy is explicitly selected by the client.

### Singleton Pattern

Ensures a class has **exactly one instance** and provides a global point of access.

```python
class Singleton:
    _instance = None

    def __new__(cls) -> "Singleton":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

**Thread-safe variant** (using Python's module-level import as natural singleton):

```python
# config.py -- module-level singleton
class _Config:
    def __init__(self) -> None:
        self.settings: dict = {}

config = _Config()  # Single instance created on import
```

**When to use**: Configuration managers, connection pools, logging. **When to avoid**: Singletons introduce global state, making testing harder. Prefer dependency injection when possible.

## Implementation

### OOD Interview Approach

A systematic 4-step method for tackling OOD interview problems:

```python
# Step 1: Identify core objects from the problem domain
# Step 2: Define responsibilities for each object
# Step 3: Design relationships (has-a, is-a, uses)
# Step 4: Apply principles (SOLID) and patterns

# Example: Parking Lot System
class ParkingSpot:
    """Individual spot with size category."""
    def __init__(self, spot_id: str, size: str) -> None:
        self.spot_id = spot_id
        self.size = size  # "compact", "regular", "large"
        self.vehicle: "Vehicle | None" = None

    def is_available(self) -> bool:
        return self.vehicle is None

    def park(self, vehicle: "Vehicle") -> bool:
        if self.is_available() and vehicle.fits(self.size):
            self.vehicle = vehicle
            return True
        return False

    def remove(self) -> "Vehicle | None":
        v = self.vehicle
        self.vehicle = None
        return v


class Vehicle:
    """Base vehicle with size constraint."""
    def __init__(self, plate: str, size: str) -> None:
        self.plate = plate
        self.size = size

    def fits(self, spot_size: str) -> bool:
        sizes = {"compact": 0, "regular": 1, "large": 2}
        return sizes[self.size] <= sizes[spot_size]


class ParkingLot:
    """Top-level system managing spots and entry/exit."""
    def __init__(self, spots: list[ParkingSpot]) -> None:
        self._spots = spots

    def find_spot(self, vehicle: Vehicle) -> ParkingSpot | None:
        for spot in self._spots:
            if spot.is_available() and vehicle.fits(spot.size):
                return spot
        return None

    def park(self, vehicle: Vehicle) -> str | None:
        spot = self.find_spot(vehicle)
        if spot and spot.park(vehicle):
            return spot.spot_id
        return None
```

### Elevator System Design

```python
from enum import Enum

class Direction(Enum):
    UP = "up"
    DOWN = "down"
    IDLE = "idle"

class ElevatorState:
    """Tracks elevator position and pending requests."""
    def __init__(self, floors: int) -> None:
        self.current_floor: int = 1
        self.direction: Direction = Direction.IDLE
        self.requests: set[int] = set()
        self.max_floor: int = floors

class Controller:
    """Schedules elevator movement using SCAN algorithm."""
    def __init__(self, elevator: ElevatorState) -> None:
        self._elevator = elevator

    def add_request(self, floor: int) -> None:
        self._elevator.requests.add(floor)

    def next_floor(self) -> int | None:
        if not self._elevator.requests:
            self._elevator.direction = Direction.IDLE
            return None
        curr = self._elevator.current_floor
        # Continue in same direction until no more requests
        if self._elevator.direction == Direction.UP:
            above = [f for f in self._elevator.requests if f > curr]
            if above:
                return min(above)
            self._elevator.direction = Direction.DOWN
        if self._elevator.direction == Direction.DOWN:
            below = [f for f in self._elevator.requests if f < curr]
            if below:
                return max(below)
            self._elevator.direction = Direction.UP
        # Pick nearest
        return min(self._elevator.requests,
                   key=lambda f: abs(f - curr))
```

**Design notes**:
- Elevator is agnostic of passengers -- only checks total weight capacity
- States: UP, DOWN, IDLE (plus maintenance states like REPAIR, INSPECTION)
- SCAN algorithm: service all requests in one direction before reversing
- Panel and Button are separate objects (ISP: buttons don't need scheduling logic)

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Identify objects first | Start of any OOD problem | Map real-world nouns to classes before coding |
| Composition over inheritance | Relating objects with flexible behavior | "Has-a" is more flexible than "is-a"; avoids fragile base class problem |
| Strategy for behavior variation | Multiple algorithms/policies for same operation | Swap behavior at runtime without modifying existing code (OCP) |
| Observer for events | Loose coupling between event producers/consumers | Subject doesn't need to know concrete observer types |
| State for lifecycle | Object behavior varies by internal state | Each state class encodes its own transitions; no giant switch/if-else |
| Singleton for shared resources | Exactly one instance needed globally | Prefer module-level instance or DI over `__new__` tricks |
| Composite for hierarchies | Tree-structured data with uniform operations | Leaf and node share the same interface |
| Factory for creation | Object creation logic is complex or varies by type | Isolate `new` from business logic |
| Interface segregation | Clients need only a subset of methods | Split fat ABCs into focused protocols |
| DI for testability | Unit testing classes with external dependencies | Inject abstractions; mock in tests |

### Common Interview Questions

- [ ] What are the SOLID principles? Explain each with an example.
- [ ] What is the difference between composition and inheritance? When to use each?
- [ ] Design a parking lot system -- identify objects, relationships, and key methods.
- [ ] Design an elevator system for a building with N floors.
- [ ] Observer vs Pub/Sub: what is the difference?
- [ ] When would you use the State pattern vs. a simple if-else chain?
- [ ] Why is Singleton considered an anti-pattern? When is it appropriate?
- [ ] How does DIP improve testability?
- [ ] Explain the Liskov Substitution Principle. Give a classic violation example.
- [ ] Design a playlist system -- what data structures and objects would you use?
- [ ] How would you refactor a class that violates SRP?
- [ ] What is the difference between State and Strategy patterns?

## Comparisons

### Design Patterns Comparison

| Aspect | Observer | Composite | State | Singleton |
|--------|----------|-----------|-------|-----------|
| **Purpose** | Event notification | Part-whole hierarchies | Behavior per state | Single instance |
| **Structure** | Subject + Observer list | Tree (Leaf + Composite) | Context + State objects | Static instance + private ctor |
| **Coupling** | Loose (subject/observer) | Uniform interface | State classes independent | Global access (tight) |
| **Extension** | Add observers freely | Add leaf/composite types | Add new states | N/A (one class) |
| **Testing** | Easy (mock observers) | Easy (mock components) | Easy (mock states) | Hard (global state) |
| **Use case** | Event systems, MVC | File trees, UI widgets | Workflow, game AI | Config, logging, pools |

### Composition vs Inheritance

| Aspect | Composition ("has-a") | Inheritance ("is-a") |
|--------|----------------------|---------------------|
| **Coupling** | Loose -- components are interchangeable | Tight -- subclass depends on superclass internals |
| **Flexibility** | Change behavior at runtime by swapping components | Fixed at compile/definition time |
| **Reuse** | Mix-and-match from multiple sources | Single inheritance chain (Python allows multiple, but it's complex) |
| **Testing** | Easy to mock individual components | Requires testing entire hierarchy |
| **When to use** | Default choice; when "has-a" relationship is natural | When there is a true "is-a" relationship AND you want polymorphism |
| **Risk** | Slightly more boilerplate (delegation) | Fragile base class problem; LSP violations |

### SOLID Principles Quick Reference

| Principle | Violation Smell | Fix Pattern |
|-----------|----------------|-------------|
| SRP | Class description uses "and" | Extract class |
| OCP | Adding feature requires editing existing code | Strategy / Template Method |
| LSP | Subclass overrides throw exceptions or no-ops | Replace inheritance with composition |
| ISP | Class implements methods it doesn't need | Split interface / use Protocols |
| DIP | High-level module imports concrete low-level module | Inject abstraction via constructor |

## Key Takeaways

- [ ] SOLID principles are guidelines, not laws -- apply judiciously based on context
- [ ] Default to composition over inheritance; use inheritance only for true "is-a" with polymorphism
- [ ] Start OOD interviews by identifying objects, then responsibilities, then relationships
- [ ] Observer decouples event producers from consumers; Pub/Sub adds a broker for further decoupling
- [ ] State pattern eliminates complex conditionals by encoding behavior in state objects
- [ ] Singleton provides convenience but hurts testability -- prefer dependency injection
- [ ] Composite enables uniform treatment of individual and composite objects in tree structures
- [ ] OCP is best achieved through Strategy pattern: pluggable behavior without modifying existing code
- [ ] DIP enables testability and swappability by depending on abstractions, not concretions
