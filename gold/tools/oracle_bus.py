"""Shared memory for the opponent-foresight upper-bound test: the seat-0 agent records its action here before the
seat-1 agent (ours) is called in the same step (fastarena calls seats in order, in one process)."""
OPP = {}
PENDING = {}
