import asyncio
import random

import logging
from .log import Log
from .timer import Timer


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
        func = getattr(self, 'on_receive_{}'.format(data['type']))
        # logging.debug('%s handling %s', func, data)
        func(data)


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


class Candidate(BaseState):
    """Raft Candidate
    — On conversion to candidate, start election:
        — Increment self term
        — Vote for self
        — Reset election timer
        — Send RequestVote RPCs to all other servers
    — If votes received from majority of servers: become leader
    — If AppendEntries RPC received from new leader: convert to follower
    — If election timeout elapses: start new election
    """

    def __init__(self, server):
        super().__init__(server)
        self.election_timer = Timer(self.election_interval,
                                    self.server.to_follower,
                                    self.server.loop)
        self.vote_count = 0

    def start(self):
        """Increment current term, vote for herself & send vote requests"""
        self.term += 1
        self.voted_for = self.server.id

        self.vote_count = 1
        self.request_vote()
        self.election_timer.start()

    def stop(self):
        self.election_timer.stop()

    def request_vote(self):
        """RequestVote RPC — gather votes
        Arguments:
            term — candidate’s term
            candidate_id — candidate requesting vote
            last_log_index — index of candidate’s last log entry
            last_log_term — term of candidate’s last log entry
        """
        data = {
            'type': 'request_vote',
            'term': self.term,
            'candidate_id': self.server.id,
            'last_log_index': self.log.last_log_index,
            'last_log_term': self.log.last_log_term
        }
        if self.server.cluster_count > 1:
            self.server.broadcast(data)
        else:
            self.server.to_leader()

    def on_receive_request_vote_response(self, data):
        """Receives response for vote request.
        If the vote was granted then check if we got majority and may
        becomeLeader
        """
        if data.get('vote_granted'):
            self.vote_count += 1
            if self.server.is_majority(self.vote_count):
                self.server.to_leader()

    def on_receive_append_entries(self, data):
        """If we discover a Leader with the same term — step down"""
        if self.term == data['term']:
            self.server.to_follower()
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

    @property
    def election_interval(self):
        return random.uniform(150, 300)


class Leader(BaseState):
    """Raft Leader
    Upon election: send initial empty AppendEntries RPCs (heartbeat) to
    each server; repeat during idle periods to prevent election timeouts

    — If command received from client: append entry to local log, respond after
        entry applied to state machine
    - If last log index ≥ next_index for a follower: send AppendEntries RPC with
        log entries starting at next_index
    — If successful: update next_index and match_index for follower
    — If AppendEntries fails because of log inconsistency:
        decrement next_index and retry
    — If there exists an N such that N > commit_index, a majority of
        match_index[i] ≥ N, and log[N].term == self term: set commit_index = N
    """

    def __init__(self, server):
        super().__init__(server)
        self.heartbeat_interval = 50
        self.step_down_missed_heartbeats = 8
        self.heartbeat_timer = Timer(self.heartbeat_interval,
                                     self.heartbeat,
                                     self.server.loop)
        self.step_down_timer = Timer(
            self.step_down_missed_heartbeats * self.heartbeat_interval,
            self.server.to_follower, self.server.loop)
        # monotonically increasing request id and response of each request
        self.request_id = 0
        self.response_map = {}

    def start(self):
        self.init_log()
        self.heartbeat_timer.start()
        self.step_down_timer.start()

    def stop(self):
        self.heartbeat_timer.stop()
        self.step_down_timer.stop()

    def init_log(self):
        self.log.next_index = {
            follower: self.log.last_log_index + 1 for follower in
            self.server.peers
        }

        self.log.match_index = {
            follower: 0 for follower in self.server.peers
        }

    async def append_entries(self, destination=None):
        """AppendEntries RPC — replicate log entries / heartbeat
        Args:
            destination — destination id

        Request params:
            term — leader’s term
            leader_id — so follower can redirect clients
            prev_log_index — index of log entry immediately preceding new ones
            prev_log_term — term of prev_log_index entry
            commit_index — leader’s commit_index

            entries[] — log entries to store (empty for heartbeat)
        """
        # Send AppendEntries RPC to destination if specified or broadcast to
        # everyone
        for dest in destination and [destination] or self.server.peers:
            data = {
                'type': 'append_entries',
                'term': self.term,
                'leader_id': self.server.id,
                'commit_index': self.log.commit_index,
                'request_id': self.request_id
            }
            # logging.debug('append_entries %s from %s', data, dest)
            next_index = self.log.next_index[dest]
            prev_index = next_index - 1

            if self.log.last_log_index >= next_index:
                data['entries'] = self.log[next_index:]
            else:
                data['entries'] = []

            data.update({
                'prev_log_index': prev_index,
                'prev_log_term': self.log[prev_index]['term'] if self.log
                and prev_index else 0
            })
            asyncio.ensure_future(self.server.send(data, dest),
                                  loop=self.server.loop)

    def on_receive_append_entries_response(self, data):
        sender_id = data['sender']
        # logging.debug('append_entries_response %s from %s', data, sender_id)

        # Count all unique responses per particular heartbeat interval
        # and step down via <step_down_timer> if leader doesn't get majority of
        # responses for  <step_down_missed_heartbeats> heartbeats
        # import ipdb; ipdb.set_trace()
        if data['request_id'] in self.response_map:
            self.response_map[data['request_id']].add(sender_id)
            answered = len(self.response_map[data['request_id']])
            if self.server.is_majority(answered + 1):
                logging.debug('leader %s step down reset', self.server.id)
                self.step_down_timer.reset()
                del self.response_map[data['request_id']]

        if not data['success']:
            self.log.next_index[sender_id] = \
                max(self.log.next_index[sender_id] - 1, 1)
        else:
            self.log.next_index[sender_id] = data['last_log_index'] + 1
            self.log.match_index[sender_id] = data['last_log_index']
            self.update_commit_index()

        # Send AppendEntries RPC to continue updating fast-forward log
        # (data['success'] == False) or in case there are new entries to sync
        # (data['success'] == data['updated'] == True)
        if self.log.last_log_index >= self.log.next_index[sender_id]:
            host, port = sender_id.split(':')
            addr = (host.strip(), port.strip())
            asyncio.ensure_future(self.append_entries(destination=addr),
                                  loop=self.server.loop)

    def update_commit_index(self):
        committed_on_majority = 0
        for index in range(self.log.commit_index + 1,
                           self.log.last_log_index + 1):
            committed_count = len([
                1 for follower in self.log.match_index
                if self.log.match_index[follower] >= index
            ])

            # If index is matched on at least half + self for
            # current term — commit. That may cause commit fails upon restart
            # with stale logs
            is_current_term = self.log[index]['term'] == self.term
            if self.server.is_majority(committed_count + 1) and is_current_term:
                committed_on_majority = index
            else:
                break

        if committed_on_majority > self.log.commit_index:
            self.log.commit_index = committed_on_majority

    def heartbeat(self):
        self.request_id += 1
        self.response_map[self.request_id] = set()
        logging.debug('%s hearbeating, request id: %s', self.server.id, self.request_id)
        asyncio.ensure_future(self.append_entries(), loop=self.server.loop)
