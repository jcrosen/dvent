"""
Event store
"""
from collections import OrderedDict
from logging import getLogger
from pprint import pprint

from pyrsistent import PClass, PRecord, field, pvector

logger = getLogger(__name__)


class IEventStoreVersionError(RuntimeError):
    """Custom RuntimeError class for IEventStore version conflicts"""

    pass


class Stream(PRecord):
    """
    Stream data container

    Only useful in the context of consuming a stream of Streams

    **Candidate for deprecation; should embed stream information in Event**
    """

    id = field(mandatory=True)

    timestamp = field(mandatory=True)

    number = field()

    @classmethod
    def generate(cls, id_, timestamp, number=None):
        return cls(**{
            'id': id_,
            'timestamp': timestamp,
            'number': number or -1
        })


class IEventStore(PClass):
    """
    Event store interface describing a minimal implementation

    Fields:
    publisher -- Function accepting saved events and "publishing" them
    """

    publisher = field()

    @classmethod
    def generate(cls, publisher=None):
        """
        Generate a new event store instance

        Keyword Arguments:
        publisher -- Function which accepts an Event as a single argument, will
                     be called with any events persisted to the store
        """
        return cls(**{
            'publisher': publisher or pprint
        })

    @staticmethod
    def check_version(expected_version=-2, last_event=None):
        """
        Verify the expected version matches the last event's version

        Raise IEventStoreVersionError if there is a conflict with expectation

        Keyword Arguments:
        expected_version -- Integer representing the expected current version of
                            an entity.  Special cases:
                              * -2 - Skip the check
                              * -1 - Expect a new entity, no existing events
                              *  0 - Same as -1, no existing events
        last_event -- The last event in the aggregate stream, used to determine
                      the actual current version for comparison to expected
        """
        # if -2 then append without checking
        if expected_version <= -2:
            return

        # if -1 or 0 then there should be no events
        if expected_version in (-1, 0):
            if last_event:
                _id = last_event.id
                raise IEventStoreVersionError(
                    'Expected new but found existing event '
                    'with id {}'.format(_id)
                )

        # if >= 1 then most recent version should match the expected version
        if expected_version >= 1:
            current_version = last_event.version if last_event else 0
            if expected_version != current_version:
                raise IEventStoreVersionError(
                    'Expected version {} but found {}'.format(
                        expected_version, current_version
                    )
                )

    def save_events(self, id_, events, expected_version=-2):
        """
        Save a `events` to stream `id_` with `expected_version` check

        **This function should be overridden in the implementing class, but the
        call to `self.check_version` should be maintained unless the underlying
        database implementation supports optimistic concurrency.**

        Arguments:
        id_ -- Stream id to which the events will be saved
        events -- Events to save to the store

        Keyword Arguments:
        expected_version -- Version checking for optimistic concurrency; see
                            `IEventStore.check_version` for details
        """
        self.check_version(
            expected_version=expected_version,
            last_event=self.get_last_event(id_)
        )
        raise NotImplementedError('Must implement save_events')

    def get_events(self, id_=None, start=0):
        """
        Return generator of ordered Events for the optionally supplied id_

        Keyword Arguments:
        id_ -- Stream id, if None will return all events in order
        start -- Integer, optionally specify a starting position in the stream
        """
        raise NotImplementedError('Must implement get_events')

    def get_last_event(self, id_):
        """
        Get the last event for the specified stream

        **This is the most naive and unoptimized implementation, consider
        overriding in the implementing class**

        Arguments:
        id_ -- Stream id
        """
        _events = list(self.get_events(id_))
        return _events[-1] if _events else None

    def get_streams(self, start=0):
        """
        Get a generator of Stream instances in persisted order

        *Considered for deprecation*
        This is too opinionated for a base class implementation;
        we would be better served by embedding the stream id in the `Event`
        class which gives better default exposure to the streams being
        ingested into the system, and would mean `get_streams` is more easily
        implemented via consumption of all events

        Keyword Arguments:
        start -- Integer, optionally specify a starting position
        """
        raise NotImplementedError('Must implement get_streams')


class InMemoryEventDB(object):
    """
    Reference db/client for use in the InMemoryEventStore interface

    Immutable append-only in-memory event database

    *Note: Not thread-safe*

    **DO NOT USE IN PRODUCTION; FOR TESTING & REFERENCE ONLY**
    """

    def __init__(self):
        """
        Initialize an empty dataset
        """
        self.streams = OrderedDict()
        self.events = pvector([])

    def write_to_stream(self, stream_id, events):
        """
        Append the `events` to the in-memory vector; update streams index

        *Note: not thread-safe*

        Arguments:
        stream_id -- Stream id to which the events apply
        events -- Events to save
        """
        # Determine the next index which corresponds to the new event
        # NOTE: This isn't atomic/safe if we encounter a race-condition;
        #       using `self.events.index` would be better but slower
        for event in events:
            # If no version is supplied then version the event here
            # This is easier than versioning on the way out
            if event.version < 0 or event.version is None:
                version = len(self.streams.get(stream_id, []))
                event = event.set('version', version)

            new_index = len(self.events)
            self.events = self.events.append(event)
            self.streams[stream_id] = self.streams\
                .setdefault(stream_id, pvector())\
                .append(new_index)

    def get_events(self, stream_id=None, start=0):
        """
        Return a generator of events from the optionally supplied stream

        Keyword Arguments:
        stream_id -- Stream id, if None return all events
        start -- Integer, optionally specify a starting position
        """
        indices = []
        if not stream_id:
            indices = range(len(self.events))
        else:
            indices = self.streams.get(stream_id) or []

        for index in indices[start:]:
            yield self.events[index]

    def get_streams(self, start=0):
        """
        Get a generator of Stream instances in persisted order

        Keyword Arguments:
        start -- Integer, optionally specify a starting position
        """
        for index, key in enumerate(list(self.streams)[start:]):
            # Because we only append data this calculation is dependable
            stream_number = index + start
            first_event = self.events[self.streams[key][0]]
            yield {
                'id': key,
                'timestamp': first_event.timestamp,
                'number': stream_number,
            }


class InMemoryEventStore(IEventStore):
    """
    In-memory append-only event store interface

    Wraps an `InMemoryEventDB` instance with the `IEventStore` interface.  This
    example is extensible to any backing database whose client can be supplied
    via `db` and interactions orchestrated in the various interface functions.

    **DO NOT USE IN PRODUCTION; FOR TESTING & REFERENCE ONLY**

    Fields:
    db -- An instance of `InMemoryEventDB`
    publisher -- Function accepting saved events and "publishing" them
    """

    db = field(type=InMemoryEventDB)

    @classmethod
    def generate(cls, publisher=None, db=None):
        """
        Generate a new in-memory event store with an existing or new database

        Keyword Arguments:
        publisher -- Function which accepts an Event as a single argument, will
                     be called with any events persisted to the store
        db -- An instance of `InMemoryEventDB`
        """
        return cls(**{
            'publisher': publisher or pprint,
            'db': db or InMemoryEventDB(),
        })

    @staticmethod
    def deserialize_event(store_event):
        """
        Convert client/db event model/data into an Event instance
        """
        # In-memory db is native so already an Event instance
        return store_event

    @staticmethod
    def serialize_event(domain_event):
        """
        Convert an Event instance into client/db event model/data
        """
        # In-memory db expects native data-structures
        return domain_event

    def save_events(self, id_, events, expected_version=-2):
        """
        Save a `events` to stream `id_` with `expected_version` check

        **This function should be overridden in the implementing class, but the
        call to `self.check_version` must be maintained**

        Arguments:
        id_ -- Stream id to which the events will be saved
        events -- Events to save to the store

        Keyword Arguments:
        expected_version -- Version checking for optimistic concurrency; see
                            `IEventStore.check_version` for details
        """
        if expected_version >= -1:
            last_event = self.get_last_event(id_)
            self.check_version(expected_version, last_event)

        # Write the events and then publish them
        try:
            self.db.write_to_stream(id_, map(self.serialize_event, events))
        except Exception as e:
            logger.critical("Failed to write events ({}): {}".format(
                ','.join(event.id for event in events),
                str(e)
            ))
        for event in events:
            try:
                self.publisher(event)
            except Exception as e:
                logger.critical("Failed publishing event {}: {}".format(
                    event, str(e)
                ))

    def get_events(self, id_=None, start=0):
        """
        Return generator of ordered Events for the optionally supplied id_

        Keyword Arguments:
        id_ -- Stream id, if None will return all events in order
        start -- Integer, optionally specify a starting position in the stream
        """
        for serialized_event in (self.db.get_events(id_, start) or []):
            yield self.deserialize_event(serialized_event)

    def get_streams(self, start=0):
        """
        Get a generator of Stream instances in persisted order

        *Considered for deprecation*
        This is too opinionated for a base class implementation;
        we would be better served by embedding the stream id in the `Event`
        class which gives better default exposure to the streams being
        ingested into the system, and would mean `get_streams` is more easily
        implemented via consumption of all events

        Keyword Arguments:
        start -- Integer, optionally specify a starting position
        """
        for stream_data in self.db.get_streams(start=start):
            yield Stream(**{
                'id': stream_data['id'],
                'timestamp': stream_data['timestamp'],
                'number': stream_data['number'],
            })
