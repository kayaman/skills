# Design Patterns — Detailed Reference

This reference expands on the 23 Gang of Four patterns introduced in the main
skill. Patterns are grouped by category; each entry lists its intent and typical
use case.

## Table of Contents

- [Creational Patterns](#creational-patterns)
  - [Abstract Factory](#abstract-factory)
  - [Builder](#builder)
  - [Factory Method](#factory-method)
  - [Prototype](#prototype)
  - [Singleton](#singleton)
- [Structural Patterns](#structural-patterns)
  - [Adapter](#adapter)
  - [Bridge](#bridge)
  - [Composite](#composite)
  - [Decorator](#decorator)
  - [Facade](#facade)
  - [Flyweight](#flyweight)
  - [Proxy](#proxy)
- [Behavioral Patterns](#behavioral-patterns)
  - [Chain of Responsibility](#chain-of-responsibility)
  - [Command](#command)
  - [Interpreter](#interpreter)
  - [Iterator](#iterator)
  - [Mediator](#mediator)
  - [Memento](#memento)
  - [Observer](#observer)
  - [State](#state)
  - [Strategy](#strategy)
  - [Template Method](#template-method)
  - [Visitor](#visitor)
- [Sources](#sources)

## Creational Patterns

### Abstract Factory

**Intent:** Provide an interface for creating families of related objects
without specifying their concrete classes.
**Use when:** A system needs to be independent of how its products are created,
or you need to enforce that a family of related objects is used together.

### Builder

**Intent:** Separate the construction of a complex object from its
representation so the same construction process can create different
representations.
**Use when:** The algorithm for creating a complex object should be independent
of the parts and how they are assembled.

### Factory Method

**Intent:** Define an interface for creating an object but let subclasses decide
which class to instantiate.
**Use when:** A class cannot anticipate the class of objects it must create, or
wants its subclasses to specify the objects it creates.

### Prototype

**Intent:** Specify the kinds of objects to create using a prototypical instance
and create new objects by copying this prototype.
**Use when:** Creating an instance is expensive or complex and a clone is more
efficient.

### Singleton

**Intent:** Ensure a class has only one instance and provide a global point of
access to it.
**Use when:** Exactly one instance of a class is needed to coordinate actions
across the system. Use sparingly — widely considered an anti-pattern when
overused.

## Structural Patterns

### Adapter

**Intent:** Convert the interface of a class into another interface clients
expect.
**Use when:** You need to use an existing class whose interface does not match
the one you need.

### Bridge

**Intent:** Decouple an abstraction from its implementation so that the two can
vary independently.
**Use when:** You want to avoid a permanent binding between an abstraction and
its implementation, or both need to be extensible through subclassing.

### Composite

**Intent:** Compose objects into tree structures to represent part-whole
hierarchies. Let clients treat individual objects and compositions uniformly.
**Use when:** You want clients to ignore the difference between composed and
individual objects.

### Decorator

**Intent:** Attach additional responsibilities to an object dynamically.
Provide a flexible alternative to subclassing for extending functionality.
**Use when:** You need to add responsibilities to individual objects without
affecting other objects of the same class.

### Facade

**Intent:** Provide a unified interface to a set of interfaces in a subsystem.
**Use when:** You want to provide a simple interface to a complex subsystem, or
there are many dependencies between clients and implementation classes.

### Flyweight

**Intent:** Use sharing to support large numbers of fine-grained objects
efficiently.
**Use when:** An application uses a large number of objects that can share
intrinsic state.

### Proxy

**Intent:** Provide a surrogate or placeholder for another object to control
access to it.
**Use when:** You need a more versatile or sophisticated reference to an object
than a simple pointer (remote proxy, virtual proxy, protection proxy).

## Behavioral Patterns

### Chain of Responsibility

**Intent:** Avoid coupling the sender of a request to its receiver by giving
more than one object a chance to handle the request.
**Use when:** More than one object may handle a request and the handler is not
known a priori.

### Command

**Intent:** Encapsulate a request as an object, thereby letting you
parameterize clients with different requests, queue or log requests, and
support undoable operations.
**Use when:** You need to parameterize objects by an action, queue operations,
or support undo.

### Interpreter

**Intent:** Given a language, define a representation for its grammar along
with an interpreter that uses the representation to interpret sentences.
**Use when:** You have a simple, well-defined grammar that needs to be
evaluated repeatedly.

### Iterator

**Intent:** Provide a way to access the elements of an aggregate object
sequentially without exposing its underlying representation.
**Use when:** You need uniform traversal of different aggregate structures.

### Mediator

**Intent:** Define an object that encapsulates how a set of objects interact.
Promotes loose coupling by preventing objects from referring to each other
explicitly.
**Use when:** A set of objects communicate in complex but well-defined ways and
you want to reduce direct dependencies.

### Memento

**Intent:** Without violating encapsulation, capture and externalize an
object's internal state so that the object can be restored to this state later.
**Use when:** You need to implement undo/redo or snapshot functionality.

### Observer

**Intent:** Define a one-to-many dependency between objects so that when one
object changes state, all its dependents are notified and updated
automatically.
**Use when:** A change to one object requires changing others and you do not
know how many objects need to change.

### State

**Intent:** Allow an object to alter its behavior when its internal state
changes. The object will appear to change its class.
**Use when:** An object's behavior depends on its state and it must change
behavior at runtime.

### Strategy

**Intent:** Define a family of algorithms, encapsulate each one, and make them
interchangeable. Strategy lets the algorithm vary independently from clients
that use it.
**Use when:** You need different variants of an algorithm or want to avoid
exposing complex, algorithm-specific data structures.

### Template Method

**Intent:** Define the skeleton of an algorithm in an operation, deferring some
steps to subclasses.
**Use when:** You want to let subclasses redefine certain steps of an algorithm
without changing the algorithm's structure.

### Visitor

**Intent:** Represent an operation to be performed on the elements of an object
structure. Visitor lets you define a new operation without changing the classes
of the elements on which it operates.
**Use when:** You need to perform many distinct and unrelated operations on
objects in a structure and want to avoid polluting their classes.

## Sources

- Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). *Design Patterns:
  Elements of Reusable Object-Oriented Software*. Addison-Wesley.
- Freeman, E., & Robson, E. (2020). *Head First Design Patterns* (2nd ed.).
  O'Reilly Media.
