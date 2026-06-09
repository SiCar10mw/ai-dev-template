# Parallel Agents

The backlog-worker remains single-item. The fleet can run multiple workers only when isolation, claiming, dispatch, and
merge serialization are enforced.

## Mandatory Mechanics

| Mechanic | Rule | Recommended Default |
|---|---|---|
| Isolated workspace | Each worker runs in its own git worktree or container. Workers never share a writable working tree. | `git worktree` under `../.agent-worktrees` |
| Atomic claim | A worker claims exactly one item through an atomic lock or queue operation. Markdown board edits are not claim locks. | `scripts/claim_backlog_item.py` |
| Concurrency cap | Dispatcher starts at most `N` active workers; excess items wait under backpressure. | `scripts/dispatch_agents.py --concurrency-cap N` |
| Merge serialization | Parallel PRs merge through a queue so gates and main-branch state cannot race. | `scripts/merge_queue.py` |
| Per-agent branches | Each worker uses its own branch. | `agent/<worker>/<item>` |
| File ownership | No two active agents own the same file path set. | paths recorded in `queue/backlog-queue.example.json` claim payloads |
| Budget ceiling | Fleet-wide token and compute ceilings are set before dispatch. | `config/fleet.example.json` |

## Claim Protocol

1. Human curates `BACKLOG.md`.
2. Dispatcher translates eligible work into `queue/backlog-queue.json`.
3. Worker calls:

   ```bash
   python scripts/claim_backlog_item.py --worker-id worker-a
   ```

4. The claim creates `.fleet/claims/<item-id>.json` with `O_CREAT | O_EXCL`.
5. A second worker racing for the same item receives no claim.
6. The worker creates its per-agent branch and isolated worktree.
7. The worker moves the item through implementation and stops for review.

## Dispatch Protocol

```bash
python scripts/dispatch_agents.py --concurrency-cap 2
```

The dispatcher reports:

- active workers
- available slots
- items to dispatch now
- backpressure queue

## Merge Protocol

```bash
python scripts/merge_queue.py --pr-id 17 --branch agent/worker-a/item-001
```

Only one queued merge is processed at a time. A serialized merge queue prevents parallel PRs from racing the same branch
protection, generated-artifact drift, dependency state, or docs state.

## Tripwire

`tests/unit/test_fleet_claims.py` asserts two workers cannot claim the same item. `scripts/check_template_conformance.py`
asserts the parallel-agent docs, fleet config, and queue scripts exist.
