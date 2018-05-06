"""
Domain event
"""
from datetime import datetime
from uuid import uuid4

from pyrsistent import PRecord, field, pmap, PMap, freeze

NoneType = type(None)


def _validate_version(version):
    return (version >= 0, 'version negative')


class Event(PRecord):
    """
    Domain event data object; immutable

    Event types should be past-tense, eg. "SomethingHappened"

    Fields:
    type -- Event type
    id -- Event id (unique)
    stream_id -- Stream id to which the event belongs (optional)
    timestamp -- datetime representing when the event happened, should be UTC
    data -- PMap of command data (optional)
    version -- Event version within its stream
    """

    type = field(type=str, mandatory=True)

    id = field(type=str, mandatory=True)

    stream_id = field(type=str)

    timestamp = field(type=datetime, mandatory=True)

    data = field(type=PMap)

    version = field(type=int, mandatory=True, invariant=_validate_version)

    @classmethod
    def generate(
        cls, event_type, data=None, id=None,
        stream_id=None, timestamp=None, version=None
    ):
        """
        Generate an Event

        `id` *must* be a UUID, will default to a random uuid4() if not supplied

        Arguments:
        event_type -- String representing the event type
        data -- PMap of command data
        id -- Event id; ideally a UUID, will default to uuid4()
        stream_id -- Stream id; ideally a UUID, optional
        timestamp -- Datetime representing when the event happened, default
                     to datetime.utcnow()
        version -- Event version within its stream
        """
        if not id:
            id = uuid4()

        return cls(**{
            'id': str(id),
            'type': event_type,
            'data': freeze(data) or pmap(),
            'stream_id': stream_id or '',
            'timestamp': timestamp or datetime.utcnow(),
            'version': version or 0,
        })
