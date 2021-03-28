from pymongo.errors import PyMongoError


class IdNotFound(PyMongoError):
    """Raised when _id was not found in the database collection."""

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = self.__doc__

    def __str__(self):
        return self.message

class InvalidArgument(Exception):
    pass

def is_owner():
    async def predicate(ctx):
        return _is_owner_check(ctx.guild.id)
    return commands.check(predicate)