
class Log:
    """Raft Log.
    Log entries:
        {term: <term>, command: <command>}
        {term: <term>, command: <command>}
        ...
        {term: <term>, command: <command>}
    """

    def __init__(self):
        # All States

        """Volatile state on all servers: index of highest log entry known to
        be committed. (initialized to 0, increases monotonically)
        """
        self.commit_index = 0

        """Volatile state on all servers: index of highest log entry applied
        to state machine (initialized to 0, increases monotonically)
        """
        self.last_applied = 0

        # Leaders
        """Volatile state on Leaders: for each server, index of the next log
        entry to send to that server (initialized to leader last log index + 1)
            {<follower>:  index, ...}
        """
        self.next_index = None

        """Volatile state on Leaders: for each server, index of highest log
        entry known to be replicated on server,initialized to 0, increases 
        monotonically. 
        {<follower>:  index, ...}
        """
        self.match_index = None
        
        self.data = []

    def __getitem__(self, index):
        return self.data[index - 1]

    def __bool__(self):
        return bool(self.data)

    def __len__(self):
        return len(self.data)

    @property
    def last_log_index(self):
        """Index of last log entry staring from _one_"""
        return len(self.data)

    @property
    def last_log_term(self):
        if self.data:
            return self.data[-1]['term']
        return 0

    def erase_from(self, index):
        self.data = self.data[:index - 1]

    def add_entries(self, entries):
        self.data = self.data + entries
