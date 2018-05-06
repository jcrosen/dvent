Feature: Event Store
An event store is a basic persistence interface that associates an ordered set
of events with a unique identifier.  It is immutable and append-only, so there
is no way to delete or update any existing data.

    Background: An Event Store
        Given a new event store

    Scenario: An event store has a basic interface
        Then the event store has a get_events function
        And the event store has a save_events function
        And the event store has a get_last_event function
        And the event store has a get_streams function

    Scenario: Save a new event stream
        When I save a new stream with some events to the store
        Then the stream is created and the events are saved

    Scenario: Save a new event stream with an id that already exists
        When I save a new stream with some events to the store
        And I try to save another stream with the same id as if it's new
        Then an error is raised
        And the duplicate event stream is not saved

    Scenario: Get a saved event stream
        When I save a new stream with some events to the store
        And I get events from the store with the same id
        Then the events returned are the same and in the same order

    Scenario: Get an event stream that doesn't exist
        When I try to get events from the store with an id that doesn't exist
        Then no events are returned

    Scenario: Save a new event to an existing stream
        When I save a new stream with some events to the store
        And I save a new event to the same stream
        Then the new event is last in the stream

    Scenario: Save a new event to an existing stream with the wrong expected version
        When I save a new stream with some events to the store
        And I save a new event to the same stream with the wrong expected version
        Then an error is raised
        And the new event is not saved

    Scenario: Get all streams in the order they were created
        When I save 2 new streams with 2 events to the store
        And I get new streams from the store
        Then all of the streams are present and in the correct order

    Scenario: Get all streams with a starting position
        When I save 5 new streams with 2 events to the store
        And I get new streams from the store starting from position 2
        Then the first returned stream is the third created
        And there are 3 streams total

    Scenario: Get all events in the order they were created
        When I save 2 new streams with 2 events to the store
        And I add a new event to the first stream
        And I get all events from the store
        Then all of the events are present and in the correct order

    Scenario: Get all events with a starting position
        When I save 2 new streams with 2 events to the store
        And I add a new event to the second stream
        And I add a new event to the first stream
        And I get all events from the store starting from position 2
        Then the first event is associated to the second stream
        And the last event is associated to the first stream
        And there are 4 events total