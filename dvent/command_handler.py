"""
Command handler
"""
from functools import lru_cache as memoize

from pyrsistent import PClass, field, pmap, PMap


class CommandHandler(PClass):
    """
    Handle commands which may include orchestrating & persisting aggregates

    Fields:
    context -- Pmap with any/all context required by the implemented handlers.
               Typically this will mean databases, config, connections, etc.
    """

    context = field(mandatory=True, type=PMap)

    @classmethod
    @memoize(maxsize=1)
    def get_handle_map(cls):
        """
        Return a map of command types to handler functions

        *If handler functions are class methods they should be defined as
        staticmethod to enforce clear separation of concerns; see
        CommandHandler.handle_noop as an example*
        """
        return pmap({
            # 'DoNothing': cls.handle_command_noop
        })

    def handle_command(self, command, context=None):
        """
        Handle a command in the provided context

        Arguments:
        command -- Command to handle

        Keyword Arguments:
        context -- Context in which to handle the command, optional override
        """
        command_fn = self.get_handle_map().get(command.type, self.handle_noop)
        context = context or self.context
        return command_fn(self.context, command) if command_fn else None

    @staticmethod
    def handle_noop(context, command):
        """
        Handle a command as a no-op; helper for modeling and testing

        Arguments:
        context -- Context in which to handle the command
        command -- Command to handle
        """
        pass
