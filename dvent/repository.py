"""
Domain repository
"""
from pyrsistent import PClass, pvector, field


class Repository(PClass):
    """
    Repository for saving and getting aggregates

    Fields:
    event_store         -- dvent.event_store.IEventStore instance
    """

    event_store = field(mandatory=True)

    def get_aggregate(self, klass, id_, apply_map=None):
        """
        Get an aggregate by class and id

        Creates a state projection from the events with the class's default
        apply map which may also be supplied for an override.  If no events are
        found returns `None`

        Arguments:
        klass -- Aggregate class
        id_ -- Aggregate id

        Keyword Arguments:
        apply_map -- a dict of event names to handler functions which
                     accept an aggregate and event; used to build a
                     projection of the aggregate from saved events
        """
        events = pvector(self.event_store.get_events(id_))

        if not events:
            return

        return klass.generate_from_events(
            id_, events, apply_map=apply_map
        )

    def save_aggregate(self, aggregate):
        """
        Save an aggregate

        Persist `uncommitted_events` to the supplied `event_store` and return
        a new aggregate with those events marked as committed

        Failure will generate an appropriate exception, generally a
        `RuntimeError` or its descendants (eg. `IEventStoreVersionError`)

        Arguments:
        aggregate -- Aggregate instance
        """
        self.event_store.save_events(
            aggregate.id,
            aggregate.uncommitted_events,
            aggregate.version
        )
        return aggregate.mark_events_committed()
