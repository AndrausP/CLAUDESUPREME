"""Full benchmark harness for orchestra-core. Read-only on repo; all state in temp dirs."""
from __future__ import annotations

import json, os, statistics, subprocess, sys, tempfile, time
from pathlib import Path
from time import perf_counter

ROOT = Path(sys.argv[1])
sys.path.insert(0, str(ROOT / "src"))

from orchestra_core.routing import Router, TaskSignals, AgentCapability
from orchestra_core.workflow import StateMachine, TransitionRequest
from orchestra_core.storage import SQLiteStore
from orchestra_core.memory import MemoryService
from orchestra_core.sanitize import sanitize, digest
from orchestra_core.models import TaskRecord, TaskStatus, MemoryType
from orchestra_core.telemetry import Event

R: dict[str, dict] = {}


def stats(name, samples_ms, n_ops=1, extra=None):
    s = sorted(samples_ms)
    p = lambda q: s[min(len(s) - 1, int(q * len(s)))]
    d = {"n": len(s), "median_ms": statistics.median(s), "p95_ms": p(0.95), "p99_ms": p(0.99),
         "min_ms": s[0], "max_ms": s[-1]}
    if n_ops > 1:
        d["ops_per_s"] = n_ops / (sum(s) / 1000)
    if extra:
        d.update(extra)
    R[name] = d
    print(f"{name:42s} med={d['median_ms']:.4f}ms p95={d['p95_ms']:.4f}ms" + (f" {d.get('ops_per_s', 0):,.0f} op/s" if n_ops > 1 else ""), flush=True)


def timeit(fn, n, warmup=50):
    for _ in range(min(warmup, n)):
        fn()
    out = []
    for _ in range(n):
        t = perf_counter(); fn(); out.append((perf_counter() - t) * 1000)
    return out


# ---------- 1. routing ----------
router = Router()
small = [AgentCapability("feature-engineer", frozenset({"backend", "tests"})),
         AgentCapability("automated-test-engineer", frozenset({"tests"})),
         AgentCapability("backend-lead", frozenset(), leader=True)]
stats("route.small(3 cands)", timeit(lambda: router.route(TaskSignals(mutation=True), {"backend", "tests"}, small), 20000))
stats("classify only", timeit(lambda: router.classify(TaskSignals(mutation=True, areas=3)), 50000))

caps = [f"c{i}" for i in range(60)]
for n in (36, 200, 1000):
    cands = [AgentCapability(f"a{i}", frozenset(caps[(i * 7) % 60:(i * 7) % 60 + 3]), leader=i % 9 == 0) for i in range(n)]
    req = set(caps[:30])
    stats(f"route.scale({n} cands, 30 caps)", timeit(lambda: router.route(TaskSignals(mutation=True, areas=3), req, cands), 300 if n < 1000 else 60, 5))

# ---------- 2. state machine ----------
req = TransitionRequest("t", 0, TaskStatus.RUNNING, TaskStatus.REVIEWING, "agent", "x", "OK", "ok")
stats("statemachine.validate", timeit(lambda: StateMachine.validate(req, []), 50000))

# ---------- 3. sanitize/digest ----------
payload = {"title": "x" * 200, "summary": "y" * 1500, "path": "C:\\Users\\x\\file.py", "api_key": "s",
           "nested": [{"k": i, "v": "z" * 50} for i in range(80)]}
stats("sanitize(medium payload)", timeit(lambda: sanitize(payload), 5000))
stats("digest(medium payload)", timeit(lambda: digest(payload), 5000))

# ---------- 4. SQLite store ----------
tmp = Path(tempfile.mkdtemp(prefix="orch-bench-"))
store = SQLiteStore(tmp / "state.db")
store.ensure_project("p", "root")
ids = []


def mk():
    t = store.create_task(TaskRecord("title", "objective", "p", "owner",
                                     acceptance_criteria=[{"id": "ac1", "status": "passed"}]))
    ids.append(t.task_id)


stats("store.create_task", timeit(mk, 1000, 10), 1000)
stats("store.get_task", timeit(lambda: store.get_task(ids[len(ids) // 2]), 3000))

chain = [TaskStatus.CLASSIFIED, TaskStatus.READY, TaskStatus.RUNNING, TaskStatus.REVIEWING,
         TaskStatus.VALIDATING, TaskStatus.APPROVED, TaskStatus.COMPLETED]
life = []
for tid in ids[:300]:
    cur, rev = TaskStatus.CREATED, 0
    t0 = perf_counter()
    for nxt in chain:
        store.transition(TransitionRequest(tid, rev, cur, nxt, "agent", "a", "OK", "ok", ("ev:1",)))
        cur, rev = nxt, rev + 1
    life.append((perf_counter() - t0) * 1000)
stats("lifecycle(7 transitions CREATED->COMPLETED)", life, extra={"per_transition_ms": statistics.median(life) / 7})

# outbox export (growth): each call re-reads whole jsonl
out = tmp / "events.jsonl"
exp = []
for i in range(20):
    for _ in range(100):
        store.enqueue_event(Event("tool.completed", "c", None, {"i": i}))
    t = perf_counter(); store.export_events(out); exp.append((perf_counter() - t) * 1000)
R["outbox.export_events(100 new, growing file)"] = {"first_ms": exp[0], "last_ms": exp[-1],
    "file_lines_end": sum(1 for _ in out.open(encoding="utf-8")), "growth_x": exp[-1] / exp[0]}
print("outbox export first/last ms", round(exp[0], 3), round(exp[-1], 3), flush=True)
db_size = (tmp / "state.db").stat().st_size + sum(p.stat().st_size for p in tmp.glob("state.db-*"))
R["store.size_after_bench"] = {"tasks": len(ids), "bytes": db_size}

# ---------- 5. memory ----------
mem = MemoryService(store)
for n_target in (100, 1000, 5000):
    store2 = SQLiteStore(tmp / f"mem{n_target}.db"); m2 = MemoryService(store2)
    ins = []
    for i in range(n_target):
        t = perf_counter()
        m2.propose(memory_type=MemoryType.PROJECT, scope="proj", title=f"Pattern number {i} repository",
                   summary=f"Use repository pattern variant {i} for persistence", content_ref=f"docs/k/{i}.md",
                   origin={"id": f"o{i}"}, tags=["pattern", f"t{i % 10}"])
        ins.append((perf_counter() - t) * 1000)
    stats(f"memory.propose (store={n_target})", ins[-100:], extra={"first100_median_ms": statistics.median(ins[:100])})
    stats(f"memory.search (store={n_target})", timeit(lambda: store2.find_memory("proj", "variant 42"), 200, 5))
    store2.close()

store.close()

# ---------- 6. hooks / CLI cold start (subprocess, what Claude Code actually pays) ----------
env = dict(os.environ, PYTHONPATH=str(ROOT / "src"), NO_COLOR="1")


def proc(args, stdin=None, n=15):
    out = []
    for _ in range(n):
        t = perf_counter()
        subprocess.run(args, input=stdin, capture_output=True, text=True, env=env, cwd=tmp)
        out.append((perf_counter() - t) * 1000)
    return out


py = sys.executable
stats("proc.python -c pass (baseline)", proc([py, "-c", "pass"]))
stats("hook.guard (allow Bash ls)", proc([py, str(ROOT / "scripts/guard_hook.py")], json.dumps({"tool_name": "Bash", "tool_input": {"command": "ls"}})))
stats("hook.guard (deny rm -rf)", proc([py, str(ROOT / "scripts/guard_hook.py")], json.dumps({"tool_name": "Bash", "tool_input": {"command": "rm -rf /"}})))
stats("hook.telemetry (disabled)", proc([py, str(ROOT / "scripts/telemetry_hook.py")], "{}"))
env["ORCHESTRA_HOOK_TELEMETRY"] = "1"
stats("hook.telemetry (enabled)", proc([py, str(ROOT / "scripts/telemetry_hook.py")], json.dumps({"tool_name": "Bash", "session_id": "s"})))
env.pop("ORCHESTRA_HOOK_TELEMETRY")
stats("hook.bootstrap (SessionStart)", proc([py, str(ROOT / "scripts/bootstrap_hook.py")], "{}", 10))
stats("cli --help", proc([py, "-m", "orchestra_core.cli", "--help"], n=10))
stats("cli route --json", proc([py, "-m", "orchestra_core.cli", "route", "--mutation", "--areas", "2", "--validations", "2", "--json"], n=10))
stats("cli agents --json", proc([py, "-m", "orchestra_core.cli", "agents", "--json"], n=10))
stats("cli status --json", proc([py, "-m", "orchestra_core.cli", "status", "--json"], n=10))
t = perf_counter()
imp = subprocess.run([py, "-X", "importtime", "-c", "import orchestra_core.cli"], capture_output=True, text=True, env=env)
top = sorted((l for l in imp.stderr.splitlines() if "|" in l and "import time" not in l),
             key=lambda l: -int(l.split("|")[1].strip()))[:8]
R["import_time_top_cumulative_us"] = [l.strip() for l in top]

# guard regex correctness spot-check (not perf, but cheap and relevant)
cases = {"rm -rf build": True, "rm -fr build": True, "rm -r -f x": True, "Remove-Item x -Recurse -Force": True,
         "git reset --hard": True, "git clean -fdx": True, "rm --recursive --force x": True,
         "del /s /q C:\\x": True, "ls -la": False, "echo format c: is bad": True}
res = {}
for cmd, expect in cases.items():
    o = subprocess.run([py, str(ROOT / "scripts/guard_hook.py")], input=json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}}),
                       capture_output=True, text=True, env=env).stdout
    res[cmd] = {"denied": "deny" in o, "expected_deny": expect}
R["guard_coverage"] = res

R["_env"] = {"python": sys.version.split()[0], "platform": sys.platform, "cpu_count": os.cpu_count()}
(Path(sys.argv[2])).write_text(json.dumps(R, indent=2, ensure_ascii=False), encoding="utf-8")
print("WROTE", sys.argv[2])
