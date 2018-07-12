import asyncio
import random

from .log import Log


class Timer(object):
    """A timer"""
    def __init__(self, interval, callback, loop):
        self.interval = interval
        self.callback = callback
        self.loop = loop
        self.handler = None

    def start(self):
        self.callback()
        self.handler = self.loop.call_latter(self.interval, self.callback)

    def reset(self):
        self.stop()
        self.start()

    def get_interval(self):
        return self.interval() if callable(self.interval) else self.interval

    def stop(self):
        self.handler.cancel()
        self.handler = None


class BaseState(object):

    def __init__(self, server):
        self.server = server
        self.log = Log()
        self.leader = None
        # latest term server has seen (initialized to 0 increases monotonically)
        self.term = 0
        # candidate_id that received vote in current term (or None)
        self.voted_for = None

    def set_leader(self, new_leader):
        self.leader = new_leader

    def on_receive_request_vote(self, data):
        """RequestVote RPC — invoked by Candidate to gather votes
        Arguments:
            term — candidate’s term
            candidate_id — candidate requesting vote
            last_log_index — index of candidate’s last log entry
            last_log_term — term of candidate’s last log entry

        Results:
            term — for candidate to update itself
            vote_granted — True means candidate received vote

        Receiver implementation:
            1. Reply False if term < self term
            2. If voted_for is None or candidateId ????,
            and candidate’s log is at least as up-to-date as receiver’s log,
            grant vote
        """

    def on_receive_request_vote_response(self, data):
        """RequestVote RPC response — description above"""

    def on_receive_append_entries(self, data):
        """AppendEntries RPC — replicate log entries / heartbeat
        Arguments:
            term — leader’s term
            leader_id — so follower can redirect clients
            prev_log_index — index of log entry immediately preceding new ones
            prev_log_term — term of prev_log_index entry
            entries[] — log entries to store (empty for heartbeat)
            commit_index — leader’s commit_index

        Results:
            term — for leader to update itself
            success — True if follower contained entry matching prev_log_index
            and prev_log_term

        Receiver implementation:
            1. Reply False if term < self term
            2. Reply False if log entry term at prev_log_index doesn't match
            prev_log_term
            3. If an existing entry conflicts with a new one, delete the entry
            and following entries
            4. Append any new entries not already in the log
            5. If leader_commit > commit_index, set commit_index =
            min(leader_commit, index of last new entry)
        """

    def on_receive_append_entries_response(self, data):
        """AppendEntries RPC response — description above"""

    def request_handler(self, data):
        """Dynamically determine the request handler by request type"""
        getattr(self, 'on_receive_{}'.format(data['type']))(data)


class Follower(BaseState):
    """Raft Follower

    — Respond to RPCs from candidates and leaders
    — If election timeout elapses without receiving AppendEntries RPC from
    current leader or granting vote to candidate: convert to candidate
    """

    def __init__(self, server):
        super().__init__(server)
        self.election_timer = Timer(self.election_interval, self.start_election,
                                    self.server.loop)

    def start(self):
        self.election_timer.start()

    def stop(self):
        self.election_timer.stop()

    @property
    def election_interval(self):
        return random.uniform(150, 300)

    def on_receive_append_entries(self, data):
        self.set_leader(data['leader_id'])

        # Reply False if log does not contain an entry at pre_log_idx
        # whose term matches prev_log_term
        pre_log_idx = data['prev_log_index']
        try:
            if (pre_log_idx and pre_log_idx > self.log.last_log_index) \
                or (pre_log_idx and self.log[pre_log_idx]['term'] !=
                    data['prev_log_term']):
                response = {
                    'type': 'append_entries_response',
                    'term': self.term,
                    'success': False,
                    'request_id': data['request_id']
                }
                asyncio.ensure_future(
                    self.server.send(response, data['sender']),
                    loop=self.server.loop)
                return
        except IndexError:
            pass

        # If an existing entry conflicts with a new one (same index but
        # different terms), delete the existing entry and all that follow it
        new_index = data['prev_log_index'] + 1
        try:
            if self.log[new_index]['term'] != data['term'] or (
                self.log.last_log_index != pre_log_idx
            ):
                self.log.erase_from(new_index)
        except IndexError:
            pass

        # It's always one entry for now
        self.log.add_entries(data['entries'])

        # Update commit index if necessary
        if self.log.commit_index < data['commit_index']:
            self.log.commit_index = min(data['commit_index'],
                                        self.log.last_log_index)

        # Return True since entry matching pre_log_idx and prev_log_term
        # was found
        response = {
            'type': 'append_entries_response',
            'term': self.term,
            'success': True,
            'last_log_index': self.log.last_log_index,
            'request_id': data['request_id']
        }
        asyncio.ensure_future(self.server.send(response, data['sender']),
                              loop=self.server.loop)

        self.election_timer.reset()

    def on_receive_request_vote(self, data):
        if self.voted_for is None and not data['type'].endswith('_response'):

            # If the logs have last entries with different terms,
            # then the log with the later term is more up-to-date.
            # If the logs end with the same term, then whichever log is longer
            # is more up-to-date.

            # Candidates' log has to be up-to-date
            if data['last_log_term'] != self.log.last_log_term:
                up_to_date = data['last_log_term'] > self.log.last_log_term
            else:
                up_to_date = data['last_log_index'] >= self.log.last_log_index

            if up_to_date:
                self.voted_for = data['candidate_id']

            response = {
                'type': 'request_vote_response',
                'term': self.term,
                'vote_granted': up_to_date
            }

            asyncio.ensure_future(self.server.send(response, data['sender']),
                                  loop=self.server.loop)

    def start_election(self):
        self.server.to_candidate()

