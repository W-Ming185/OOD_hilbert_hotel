Based on the assignment requirements, I’d structure it like this:

Phase 1 — Requirements Analysis
Read the specification and extract:
functional requirements
edge cases
constraints
required experiments
required outputs/files
Identify the actor: likely Hotel Manager
Identify the major use cases
Examples: initialize system, add/remove guest, add/remove building, search, show occupied rooms, report load balance, run experiments, export CSV
Deliverable: requirements checklist + use-case list
Gate: you should be able to explain what the system must do without talking about classes yet.
Phase 2 — Use Case Design
Draw the Use Case Diagram
Decide which actions are real actor goals and which are internal behavior
Example question:
Is Move Guest a separate use case?
Or is migration part of Add Building / Remove Building?

Write a short flow for important use cases:

Add Building
  → validate building ID
  → modify ring
  → determine affected guests
  → update assignments
  → report migrations
Deliverable: use-case diagram + important use-case descriptions
Gate: every required feature in the assignment should map to a use case or supporting system behavior.
Phase 3 — Domain Rules and Invariants
Extract rules that must always remain true

For example:

Guest ID (c, s) must be unique
Node ID must be unique
room_no depends only on guest ID
Python hash() cannot be the main hash
adding a guest must not move existing guests
adding a node → movers only move into new node
removing a node → guests from other nodes stay
final building cannot be removed
Also understand:
Cantor pairing
deterministic 64-bit hashing
consistent hashing
virtual nodes
wrap-around
collision ordering
Deliverable: invariant/business-rule document
Gate: if I give you an operation, you should be able to tell me what rules could be violated.
Phase 4 — Architecture and Detailed Design
Decide the major components

Likely areas:

CLI / main
     ↓
HotelSystem
  ↙      ↘
Guest    HashRing
            ↓
         Hashing
Decide class responsibilities
Draw the Class Diagram
Choose data structures:
where dict makes sense
where sorted list makes sense
where set might help
how reverse lookup works
Define interfaces between components

Example design question:

Should HashRing know about actual Guest objects, or should it only receive a hash position and return a node ID?

Deliverables: architecture diagram, class diagram, data-structure decisions
Gate: every class should have one clear responsibility and you should be able to justify why it exists.
Phase 5 — Core Algorithm Implementation
Build the foundations before the full application.
deterministic SHA-based hashing
convert hash to 64-bit ring position
room-number calculation
virtual-node creation
sorted ring representation
successor lookup
wrap-around
collision handling
Start with tiny deterministic tests, including the small-ring example from the assignment.
Deliverable: working routing engine
Gate: given a fake ring and guest position, your code always selects the correct building.
Phase 6 — Application Features
Now build the real workflows on top of the core.
initialize hotel
add one guest
add guest group
remove guest
search (c,s) → (node_id, room_no)
reverse search (node_id, room_no) → (c,s)
show occupied rooms
add building
remove building
migration reporting
load-balance statistics
CSV export
CLI/menu last, not first
Deliverable: complete functional system
Gate: all mandatory use cases work without depending on manual fixes.
Phase 7 — Testing and Verification
Write automated tests using assert or unittest
Test:
duplicates
invalid deletion
deleting last building
batch rollback
wrap-around
exact vnode position
vnode collisions
K = 0
migrations
room number stability
CSV row count
Verify the major invariants after each topology change.
Deliverable: automated test suite
Gate: core rules pass before you benchmark anything.
Phase 8 — Benchmarking and Experiments
The assignment requires experiments around K, N, and V.
Experiment A: vary guest count K
Experiment B: vary number of buildings N
Experiment C: vary virtual nodes V

Measure:

time
memory
migration rate
load balance / CV

Compare:

Consistent Hashing
      vs
hash mod N
Use the same guests, nodes, salts, Python version, and machine for fair comparison.
Deliverables: experiment CSVs + graphs
Gate: experiments must be reproducible.
Phase 9 — Complexity Analysis
Only now analyze the code you actually wrote
Analyze:
ring construction
guest insertion/removal
routing lookup
search indexes
sorting rooms
add/remove building
migration detection
memory

Keep the important distinction:

number of guests moved
≠
computational complexity
Deliverable: Big-O table with assumptions
Gate: every Big-O claim should point back to your real implementation.
Phase 10 — Final Documentation and Delivery
Update diagrams to match the final system

Write:

README
architecture explanation
class responsibilities
data structures
algorithms
Big-O
tests
experiments
limitations
team contribution

Package:

code
tests
README
report Word/PDF
CSV files
graphs
Deliverable: final ZIP ready for submission.

The overall engineering lifecycle is therefore:

Requirements
    ↓
Use Cases
    ↓
Rules / Invariants
    ↓
Architecture
    ↓
Class + Data Structure Design
    ↓
Core Algorithms
    ↓
Application Features
    ↓
Testing
    ↓
Experiments
    ↓
Big-O
    ↓
Documentation

For us specifically, I would say you are currently around Phase 2–3. You have started identifying use cases and you are learning the domain concepts such as virtual nodes. I would not start implementing HotelSystem yet.

Your next milestone should be: finish the use-case model, then extract the system invariants. After that, we move into architecture and the class diagram.