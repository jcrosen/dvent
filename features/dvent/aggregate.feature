Feature: Domain Aggregate
A domain object that represents a Domain Entity as an ordered and consistent
series of Domain Events which it generates as a result of validating and
evaluating Domain Commands.  In addition to the Entity's guarantee of identity,
an Aggregate also has a type which differentiates it from other Entities and
isolates the expectation of Events and Commands it will apply and handle.

An aggregate does not have any mechanism for persisting the events in its
collection, but it does provide an interface to collect, return, and flush any
uncommitted events, and also allows version management for both the aggregate
and its events through the interface.

    Scenario: An aggregate has an additional set of values
        When I generate a new aggregate
        Then the aggregate has a id value
        And the aggregate has a type value
        And the aggregate has a events value
        And the aggregate has a uncommitted_events value
        And the aggregate has a state value

    Scenario: Applying an event to an aggregate adds the event to it's uncommitted events
        Given an aggregate
        When I apply a new domain event to the aggregate
        Then the aggregate has uncommitted events

    Scenario: Applying an event to an aggregate changes it's version
        Given an aggregate and its version
        When I apply a new domain event to the aggregate
        Then the aggregate uncommitted version is incremented
        And the aggregate version still matches the previous version

    Scenario: Marking an aggregate's events as committed changes it's expected version
        Given an aggregate and its version
        When I apply a new domain event to the aggregate
        And I mark the aggregate's events as committed
        Then the aggregate version is incremented
        And the aggregate uncommitted version is incremented

    Scenario: Applying a state-altering event alters the state
        Given an aggregate and its state
        When I apply a new state-changing domain event to the aggregate
        Then the aggregate's state is changed
