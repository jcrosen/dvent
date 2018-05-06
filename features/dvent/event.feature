Feature: Domain Event
A domain object that defines an event in the past (something that happened) that
domain experts care about.  A domain event is always expressed in past tense and
is generally the result of a evaluating a Domain Command.

An example of a domain event might be "Track Added" or "Track Title Changed".

    Scenario: An event has an id and additional set of values
        When I generate a new event
        Then the event has a id value
        Then the event has a stream_id value
        And the event has a type value
        And the event has a timestamp value
        And the event has a data value
        And the event has a version value
