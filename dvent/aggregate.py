"""
Domain aggregate
"""
from functools import lru_cache as memoize
from uuid import UUID, uuid4

from pyrsistent import PClass, field, pmap, PMap, pvector_field, pvector

from dvent.event import Event


class Aggregate(PClass):
    """
    Aggregate base class

    Intended as a base class for all domain aggregates

    Fields:
    id -- Aggregate id
    events -- Committed events modeled as PVector
    uncommitted_events -- Uncommitted events modeled as PVector
    state -- Current state projection modeled as PMap
    """

    id = field(type=str, mandatory=True)

    events = pvector_field(Event)

    uncommitted_events = pvector_field(Event)

    state = field(type=PMap)

    # Private
    def _version(self, committed=True):
        """
        Get the current version of an aggregate

        If `committed` is False then include uncommitted events
        """
        _events = self.events

        if not committed:
            _events += self.uncommitted_events

        return _events[-1].version if _events else 0

    # Public
    @classmethod
    def generate(cls, id=None):
        """
        Return a new aggregate data structure

        Parameters:
        id_ -- UUID, defaults to a randomly generated UUID if not specified
        """
        if not id:
            id = uuid4()
        else:
            # Must be a valid UUID string
            id = UUID(id)

        return cls(**{
            'id': str(id),
            'events': pvector(),
            'uncommitted_events': pvector(),
            'state': pmap(),
        })

    @classmethod
    def generate_from_events(
        cls, id_, events, committed=True, apply_map=None
    ):
        """
        Return an aggregate from applying the supplied events and apply_map

        Parameters:
        apply_map -- A dict of event_type keys to handler functions
        id_ -- unique identity; required because an aggregate must have identity
               in order to have events associated
        events -- The events to apply
        committed -- If True then the events are added as if committed
        """
        apply_map = apply_map or cls.get_apply_map()
        aggregate = cls.generate(id_)
        return aggregate.apply_events(
            events, committed=committed, apply_map=apply_map
        )

    @classmethod
    @memoize(maxsize=1)
    def get_apply_map(cls):
        """
        Return a map of event types to apply functions

        *If apply functions are class methods they should be defined as
        staticmethod to enforce clear separation of concerns; see
        Aggregate.apply_noop as an example*
        """
        return pmap({
            # 'NothingHappened': cls.apply_noop
        })

    def apply_event(self, event, committed=False, apply_map=None):
        """
        Apply an event to the aggregate, returning a new instance

        Versions the event and aggregate & updates state

        Arguments:
        event -- Event instance to apply

        Keyword Arguments:
        committed -- If True then apply the events as committed
        apply_map -- If supplied override definition of `self.get_apply_map`
        """
        # Get the state-update
        _apply_map = apply_map or self.get_apply_map()
        apply_fn = _apply_map.get(event.type, self.apply_noop)

        # Apply state-changes
        _aggregate = apply_fn(self, event) if apply_fn else self

        # Version the event
        if not event.version:
            event = event.set('version', (self.uncommitted_version + 1))

        if not committed:
            _aggregate = _aggregate.set(
                'uncommitted_events',
                _aggregate.uncommitted_events + (event,)
            )
        else:
            _aggregate = _aggregate.set(
                'events',
                _aggregate.events + (event,)
            )

        return _aggregate

    def apply_events(self, events, committed=False, apply_map=None):
        """
        Apply multiple events to an aggregate, delegates to `apply_event`
        """
        _aggregate = self
        for event in events:
            _aggregate = _aggregate.apply_event(
                event, committed=committed, apply_map=apply_map
            )
        return _aggregate

    @property
    def type(self):
        return self.__class__.__name__

    @property
    def version(self):
        return self._version()

    @property
    def uncommitted_version(self):
        return self._version(committed=False)

    def set_state(self, key, value):
        """
        Return a new aggregate with its state updated by key/value
        """
        return self.set('state', self.state.set(key, value))

    def mark_events_committed(self):
        """
        Return new aggregate with `uncommitted_events` moved to `events`

        Also effectively updates the committed version of the aggregate
        """
        return self\
            .set('events', self.events + self.uncommitted_events)\
            .set('uncommitted_events', pvector())

    @staticmethod
    def apply_noop(aggregate, event):
        """
        Aggregate event handler function that acts as a no-op

        Event handlers that do something should return a new aggregate with
        updated state.  For example:

            @staticmethod
            def apply_hello_world(aggregate):
                return aggregate.set_state('hello', 'world')

        Arguments:
        aggregate -- Aggregate instance to which the event will be applied
        event -- Event instance to "apply" to the `aggregate`
        """
        return aggregate
