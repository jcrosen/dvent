"""
Domain command
"""
from datetime import datetime

from pyrsistent import PRecord, field, pmap, PMap


class Command(PRecord):
    """
    Domain command data object; immutable

    Command types should be present-tense actions, eg. "DoSomething"

    Fields:
    type -- Command type
    timestamp -- datetime representing when the command is expressed/created,
                 should be UTC
    data -- PMap of command data (optional)
    """

    type = field(type=str, mandatory=True)

    timestamp = field(type=datetime, mandatory=True)

    data = field(type=PMap, mandatory=True)

    @classmethod
    def generate(
        cls, command_type, data=None, timestamp=None
    ):
        """
        Generate a command

        Arguments:
        command_type -- String representing the command type
        timestamp -- Datetime representing when the command is expressed/created
        data -- PMap of command data
        """
        return Command(**{
            'type': command_type,
            'timestamp': timestamp or datetime.utcnow(),
            'data': data or pmap(),
        })
