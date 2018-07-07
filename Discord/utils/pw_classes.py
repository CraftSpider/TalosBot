
import datetime as dt


class PW:
    """Represents a Productivity War"""

    __slots__ = ('start', 'end', 'members')

    def __init__(self):
        """Creates a PW object, with empty variables."""
        self.start = None
        self.end = None
        self.members = []

    def get_started(self):
        """Gets whether the PW is started"""
        return self.start is not None

    def get_finished(self):
        """Gets whether the PW is ended"""
        return self.end is not None

    def begin(self, tz):
        """Starts the PW, assumes it isn't started"""
        self.start = dt.datetime.now(tz=tz)
        for member in self.members:
            if not member.get_started():
                member.begin(self.start)

    def finish(self, tz):
        """Ends the PW, assumes it isn't ended"""
        self.end = dt.datetime.now(tz=tz)
        for member in self.members:
            if not member.get_finished():
                member.finish(self.end)

    def join(self, member, tz):
        """Have a new member join the PW."""
        if PWMember(member) not in self.members and self.get_finished() is not True:
            new_mem = PWMember(member)
            if self.get_started():
                new_mem.begin(dt.datetime.now(tz=tz))
            self.members.append(new_mem)
            return True
        else:
            return False

    def leave(self, member, tz):
        """Have a member in the PW leave the PW."""
        if PWMember(member) in self.members:
            for user in self.members:
                if user == PWMember(member):
                    if user.get_finished():
                        return 2
                    elif user.get_started():
                        user.finish(dt.datetime.now(tz=tz))
                    else:
                        self.members.remove(user)
                        break
            # check if anyone isn't finished
            for user in self.members:
                if not user.get_finished():
                    return 0
            # if everyone is finished, end the pw
            self.finish(tz)
            return 0
        else:
            return 1


class PWMember:
    """Represents a single member of a PW"""

    __slots__ = ('user', 'start', 'end')

    def __init__(self, user):
        """Create a PWMember object with given member"""
        self.user = user
        self.start = None
        self.end = None

    def __str__(self):
        """Convert PWMember to a string"""
        return str(self.user)

    def __eq__(self, other):
        """Check equality with another PWMember instance"""
        return isinstance(other, PWMember) and self.user == other.user

    def get_len(self):
        """Get the length of time this member was in the PW"""
        if self.end is None or self.start is None:
            return -1
        else:
            return self.end - self.start

    def get_started(self):
        """Get whether this member has started a PW"""
        return self.start is not None

    def get_finished(self):
        """Get whether this member has finished a PW"""
        return self.end is not None

    def begin(self, time):
        """Set this member as having started a PW"""
        if not isinstance(time, (dt.datetime, dt.time)):
            raise ValueError("Time must be a datetime or time instance")
        self.start = time.replace(microsecond=0)

    def finish(self, time):
        """Set this member as having finished a PW"""
        if not isinstance(time, (dt.datetime, dt.time)):
            raise ValueError("Time must be a datetime or time instance")
        self.end = time.replace(microsecond=0)