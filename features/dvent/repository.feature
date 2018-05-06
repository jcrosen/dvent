Feature: Domain Repository
A repository provides an explicit interface to persist and retrieve domain
aggregates.  The repository allows for development and integration of
interchangeable storage interfaces.  So the domain aggregates can be persisted
to the best storage for the given context (eg. an in-memory database for
testing and on-disk for production).

    Scenario: A repository implements some core functions
        Given a new repository
        Then the repository has a get_aggregate function
        And the repository has a save_aggregate function

    Scenario: Save a new aggregate
        Given a new repository
        And a new aggregate with uncommitted events
        When I save the aggregate to the repository
        Then the aggregate has no uncommitted events
        And the aggregate can be retrieved by id from the repository

    Scenario: Save an existing aggregate with new events
        Given a new repository
        And an existing aggregate
        And a new domain event
        When I apply the event to the aggregate
        And I save the aggregate to the repository
        Then the aggregate has no uncommitted events
        And the aggregate can be retrieved by id from the repository

    Scenario: Saving an aggregate with the incorrect expected version will fail
        Given a new repository
        And an existing aggregate
        And another copy of that aggregate
        When I apply a new event to the aggregate
        And I save the aggregate to the repository
        And I apply a new event to the aggregate copy
        And I try to save the aggregate copy
        Then an error is raised

    Scenario: Retrieving an aggregate by id
        Given a new repository
        And an existing aggregate
        When I retrieve the aggregate from the repository
        Then the aggregate is returned

    Scenario: Retrieving an aggregate that does not exist will return nothing
        Given a new repository
        When I try to retrieve an aggregate from the repository
        Then no aggregate is returned
