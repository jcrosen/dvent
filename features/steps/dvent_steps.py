"""
Feature execution steps for the base domain modeling objects
"""
from itertools import chain
from uuid import uuid4
from behave import given, when, then
from pyrsistent import v as make_vector, pmap, pvector
from dvent.aggregate import Aggregate
from dvent.command import Command
from dvent.event import Event
from dvent.event_store import InMemoryEventStore
from dvent.repository import Repository

# Dummy apply map that returns the aggregate unchanged
_apply_map = pmap({'EventHappened': Aggregate.apply_noop})


def _generate_dummy_aggregate():
    _aggregate = Aggregate.generate()
    _event = Event.generate('EventHappened')
    _aggregate = _aggregate.apply_event(
        _event, committed=True, apply_map=_apply_map
    )
    return _aggregate


@given(u'an aggregate')
def _given_an_aggregate(context):
    context.aggregate = _generate_dummy_aggregate()


@given(u'an aggregate and its version')
def _given_an_aggregate_and_its_version(context):
    context.aggregate = _generate_dummy_aggregate()
    context.previous_version = context.aggregate.version


@when(u'I generate a new aggregate')
def _when_i_generate_a_new_aggregate(context):
    context.aggregate = Aggregate.generate()


@then(u'the aggregate has a {key} value')
def _then_the_aggregate_has_an_id_attribute(context, key):
    assert hasattr(context.aggregate, key)


@when(u'I apply a new domain event to the aggregate')
def _when_i_apply_a_new_domain_event_to_the_aggregate(context):
    context.event = Event.generate('EventHappened')
    context.aggregate = context.aggregate.apply_event(context.event)


@given(u'an aggregate and its state')
def _given_an_aggregate_and_its_state(context):
    context.aggregate = _generate_dummy_aggregate()
    context.previous_state = context.aggregate.state


@when(u'I apply a new state-changing domain event to the aggregate')
def _when_i_apply_a_new_state_changing_domain_event_to_the_aggregate(context):
    context.event = Event.generate('EventHappened')
    _key = context.expected_state_key = 'hello'
    _value = context.expected_state_value = 'world'
    apply_map = pmap({
        'EventHappened': lambda agg, *a, **kw: agg.set_state(_key, _value)
    })
    context.aggregate = context.aggregate.apply_event(
        context.event, apply_map=apply_map
    )


@then(u'the aggregate\'s state is changed')
def _then_the_aggregate_state_is_changed(context):
    _key, _value = context.expected_state_key, context.expected_state_value
    assert context.aggregate.state[_key] == _value


@then(u'the aggregate has uncommitted events')
def _then_the_aggregate_has_uncommitted_events(context):
    assert context.aggregate.uncommitted_events


@then(u'the aggregate uncommitted version is incremented')
def _then_the_aggregate_uncommitted_version_is_incremented(context):
    current_version = context.aggregate.uncommitted_version
    assert current_version == (context.previous_version + 1)


@then(u'the aggregate version still matches the previous version')
def _then_the_aggregate_version_still_matches_the_previous_version(context):
    assert context.aggregate.version == context.previous_version


@when(u'I mark the aggregate\'s events as committed')
def _when_i_mark_the_aggregates_events_as_committed(context):
    context.aggregate = context.aggregate.mark_events_committed()


@then(u'the aggregate version is incremented')
def _then_the_aggregate_expected_version_is_incremented(context):
    current_version = context.aggregate.version
    assert current_version == (context.previous_version + 1)


@when(u'I generate a new command')
def _when_i_generate_a_new_command(context):
    context.command = Command.generate('DoSomething')


@then(u'the command has a {key} value')
def _then_the_command_has_a_value(context, key):
    assert key in context.command


@when(u'I generate a new event')
def _when_i_generate_a_new_event(context):
    context.event = Event.generate('EventHappened')


@then(u'the event has a {key} value')
def _then_the_event_has_a_value(context, key):
    assert key in context.event


@then(u'the event store has a {fn_name} function')
def _then_the_event_store_has_a_get_events_function(context, fn_name):
    assert hasattr(context.event_store, fn_name)


@given(u'a new event store')
def _given_a_new_event_store(context):
    context.event_store = InMemoryEventStore.generate()


@when(u'I save a new stream with some events to the store')
def _when_i_save_a_new_stream_with_some_events_to_the_store(context):
    context.stream_id = str(uuid4())
    context.events = make_vector(
        Event.generate('EventHappened', version=1),
        Event.generate('EventHappened', version=2),
    )
    context.event_store.save_events(
        context.stream_id, context.events, expected_version=-1
    )


@then(u'the stream is created and the events are saved')
def _then_the_stream_is_created_and_the_events_are_saved(context):
    assert (
        pvector(context.event_store.get_events(context.stream_id)) ==
        context.events
    )


@when(u'I try to save another stream with the same id as if it\'s new')
def _when_i_try_to_save_another_stream_with_the_same_id_as_if_its_new(context):
    dupe_stream_events = reversed(context.events)
    try:
        context.event_store.save_events(
            context.stream_id, dupe_stream_events, -1
        )
    except RuntimeError as e:
        context.error = e


@then(u'the duplicate event stream is not saved')
def _then_the_duplicate_event_stream_is_not_saved(context):
    assert (
        pvector(context.event_store.get_events(context.stream_id)) ==
        context.events
    )


@when(u'I get events from the store with the same id')
def _when_i_get_events_from_the_store_with_the_same_id(context):
    context.retrieved_events = pvector(context.event_store.get_events(
        context.stream_id
    ))


@then(u'the events returned are the same and in the same order')
def _then_the_events_returned_are_the_same_and_in_the_same_order(context):
    assert context.events == context.retrieved_events


@when(u'I try to get events from the store with an id that doesn\'t exist')
def _when_i_try_to_get_events_with_id_that_doesnt_exist(context):
    context.retrieved_events = pvector(context.event_store.get_events(
        'Idonotexist'
    ))


@then(u'no events are returned')
def _then_no_events_are_returned(context):
    assert not context.retrieved_events


@when(u'I save a new event to the same stream')
def _when_i_save_a_new_event_to_the_same_stream(context):
    context.new_event = Event.generate(
        'NewEventHappened', version=(len(context.events) + 1)
    )
    context.event_store.save_events(
        context.stream_id, (context.new_event,), -2
    )


@then(u'the new event is last in the stream')
def _then_the_new_event_is_last_in_the_stream(context):
    context.retrieved_events = pvector(context.event_store.get_events(
        context.stream_id
    ))
    assert context.retrieved_events[-1] == context.new_event
    assert len(context.retrieved_events) == len(context.events) + 1


@when(u'I save a new event to the same stream with the wrong expected version')
def _when_i_save_new_event_to_same_stream_with_wrong_expected_version(context):
    context.new_event = Event.generate(
        'NewEventHappened', version=(len(context.events) + 1)
    )
    try:
        context.event_store.save_events(
            context.stream_id, (context.new_event,), 0  # Version should be 2
        )
    except RuntimeError as e:
        context.error = e


@then(u'the new event is not saved')
def _then_the_new_event_is_not_saved(context):
    context.retrieved_events = pvector(context.event_store.get_events(
        context.stream_id
    ))
    assert context.retrieved_events[-1] != context.new_event
    assert len(context.retrieved_events) == len(context.events)


@when(u'I get new streams from the store')
def _when_i_get_new_streams_from_the_store(context):
    context.new_streams = tuple(context.event_store.get_streams())


@then(u'all of the streams are present and in the correct order')
def _then_all_of_the_streams_are_in_the_list_of_stream_ids(context):
    new_ids = tuple(s.id for s in context.new_streams)
    assert new_ids == context.stream_ids


@when(u'I save {num_streams} new streams with some events to the store')
def _when_i_save_new_streams_with_events_to_the_store(context, num_streams):
    num_streams = int(num_streams)
    context.stream_ids = tuple(str(uuid4()) for _ in range(num_streams))
    for stream_id in context.stream_ids:
        events = make_vector(
            Event.generate('EventHappened', version=1),
            Event.generate('EventHappened', version=2),
        )
        context.event_store.save_events(
            stream_id, events, expected_version=-1
        )


@when(u'I get new streams from the store starting from position {pos}')
def _when_i_get_new_streams_from_the_store_starting_from_pos(context, pos):
    pos = int(pos)
    context.new_streams = tuple(context.event_store.get_streams(start=pos))


@then(u'the first returned stream is the third created')
def _then_the_first_returned_stream_is_the_third_created(context):
    assert context.new_streams[0].id == context.stream_ids[2]


@then(u'there are {num_streams} streams total')
def _then_there_are_num_streams_total(context, num_streams):
    num_streams = int(num_streams)
    assert len(context.new_streams) == num_streams


@when(u'I get all events from the store')
def _when_i_get_all_events_from_the_store(context):
    context.all_events = pvector(context.event_store.get_events())


@then(u'all of the events are present and in the correct order')
def _then_all_of_the_events_are_present_and_in_the_correct_order(context):
    stream_events = pvector(chain(*[
        context.event_store.get_events(id_) for id_ in context.stream_ids
    ]))
    stream_event_ids = set([e.id for e in stream_events])
    all_events_ids = set([e.id for e in context.all_events])

    # all ids present
    assert not stream_event_ids.difference(all_events_ids)

    assert (
        context.all_events ==
        sorted(context.all_events, key=lambda e: e.timestamp)
    )


@when(u'I save {num_streams} new streams with {num_events} events to the store')
def _when_i_save_a_new_stream_with_events_to_the_store(
    context, num_streams, num_events
):
    num_streams = int(num_streams)
    num_events = int(num_events)
    context.stream_ids = tuple(str(uuid4()) for _ in range(num_streams))
    for stream_id in context.stream_ids:
        events = tuple(
            Event.generate('SomethingHappened') for _ in range(num_events)
        )
        context.event_store.save_events(stream_id, events)


@when(u'I add a new event to the first stream')
def _when_i_add_a_new_event_to_the_first_created_stream(context):
    context.event_store.save_events(
        context.stream_ids[0], (Event.generate('AnotherEventHappened'),)
    )


@when(u'I add a new event to the second stream')
def _when_i_add_a_new_event_to_the_second_stream(context):
    context.event_store.save_events(
        context.stream_ids[1], (Event.generate('AnotherEventHappened'),)
    )


@when(u'I get all events from the store starting from position {pos}')
def _when_i_get_all_events_from_the_store_starting_from_position(context, pos):
    pos = int(pos)
    context.all_events = pvector(context.event_store.get_events(start=pos))


@then(u'the first event is associated to the second stream')
def _then_the_first_event_is_associated_to_the_second_stream(context):
    second_stream_id = context.stream_ids[1]
    stream_events = context.event_store.get_events(second_stream_id)
    assert context.all_events[0] in stream_events


@then(u'the last event is associated to the first stream')
def _then_the_last_event_is_associated_to_the_first_stream(context):
    first_stream_id = context.stream_ids[0]
    stream_events = context.event_store.get_events(first_stream_id)
    assert context.all_events[-1] in stream_events


@then(u'there are {num_events} events total')
def _then_there_are__events_total(context, num_events):
    num_events = int(num_events)
    assert len(context.all_events) == num_events


@given(u'a new repository')
def _given_a_new_repository(context):
    context.event_store = InMemoryEventStore.generate()
    context.repository = Repository(event_store=context.event_store)


@then(u'the repository has a {fn_name} function')
def _then_the_repository_has_a_fn_name_function(context, fn_name):
    assert hasattr(context.repository, fn_name)


@given(u'a new aggregate with uncommitted events')
def _given_a_new_aggregate_with_uncommitted_events(context):
    context.events = make_vector(
        Event.generate('EventHappened'), Event.generate('EventHappened')
    )
    context.aggregate = Aggregate.generate()
    context.aggregate = context.aggregate.apply_events(
        context.events, apply_map=_apply_map
    )


@when(u'I save the aggregate to the repository')
def _when_i_save_the_aggregate_to_the_repository(context):
    context.aggregate = context.repository.save_aggregate(context.aggregate)


@then(u'the aggregate has no uncommitted events')
def _then_the_aggregate_has_no_uncommitted_events(context):
    assert len(context.aggregate.uncommitted_events) == 0


@then(u'the aggregate can be retrieved by id from the repository')
def _then_the_aggregate_can_be_retrieved_by_id_from_the_repository(context):
    aggregate = context.repository.get_aggregate(
        Aggregate, context.aggregate.id
    )
    assert aggregate.events


@given(u'an existing aggregate')
def _given_an_existing_aggregate(context):
    context.events = make_vector(
        Event.generate('EventHappened'), Event.generate('EventHappened')
    )
    _aggregate = Aggregate.generate()
    _aggregate = _aggregate.apply_events(
        context.events, apply_map=_apply_map
    )
    context.aggregate = context.repository.save_aggregate(_aggregate)


@given(u'a new domain event')
def _given_a_new_domain_event(context):
    context.new_event = Event.generate('EventHappened')


@when(u'I apply the event to the aggregate')
def _when_i_apply_the_event_to_the_aggregate(context):
    context.aggregate = context.aggregate.apply_event(context.new_event)


@given(u'another copy of that aggregate')
def _given_another_copy_of_that_aggregate(context):
    context.aggregate_copy = context.aggregate


@when(u'I apply a new event to the aggregate')
def _when_i_apply_a_new_event_to_the_aggregate(context):
    context.aggregate = context.aggregate.apply_event(
        Event.generate('EventHappened')
    )


@when(u'I apply a new event to the aggregate copy')
def _when_i_apply_a_new_event_to_the_aggregate_copy(context):
    context.aggregate_copy = context.aggregate_copy.apply_event(
        Event.generate('EventHappened')
    )


@when(u'I try to save the aggregate copy')
def _when_i_try_to_save_the_aggregate_copy(context):
    try:
        context.repository.save_aggregate(context.aggregate_copy)
    except RuntimeError as e:
        context.error = e


@when(u'I retrieve the aggregate from the repository')
def _when_i_retrieve_the_aggregate_from_the_repository(context):
    context.retrieved_aggregate = context.repository.get_aggregate(
        Aggregate, context.aggregate.id
    )


@then(u'the aggregate is returned')
def _then_the_aggregate_is_returned(context):
    context.aggregate == context.retrieved_aggregate


@when(u'I try to retrieve an aggregate from the repository')
def _when_i_try_to_retrieve_an_aggregate_from_the_repository(context):
    context.retrieved_aggregate = context.repository.get_aggregate(
        Aggregate, 'Idontexist'
    )


@then(u'no aggregate is returned')
def _then_no_aggregate_is_returned(context):
    assert context.retrieved_aggregate is None


@then(u'an error is raised')
def _then_an_error_is_raised(context):
    assert isinstance(context.error, Exception)
