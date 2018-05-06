Feature: Domain Command
A domain object that espresses an intent to alter a domain's state in some way.
A domain command is generally a command explicitly exposed in a public interface
(eg. users or API consumers).

An example of a domain command might be "Add Track" or "Change Track Title".

    Scenario: A command has a set of values
        When I generate a new command
        Then the command has a type value
        And the command has a timestamp value
        And the command has a data value
