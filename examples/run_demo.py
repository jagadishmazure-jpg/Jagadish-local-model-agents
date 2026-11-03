"""Demo: run a small fixed task set through the pipeline and print
the numbers the README quotes. All tasks are fictional; the model is
simulated; nothing leaves the device and nothing is downloaded.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from local_model_agents.cost import CostModel
from local_model_agents.pipeline import LocalAgentPipeline

TASKS = [
    "summarize the weekly status notes for the Vexmere Edge field team",
    "classify this ticket: the warehouse scanner is offline",
    "draft a reply to a customer asking about delivery times",
    "explain how the local routing decision works",
    "blorpt zzz unknown task with no matching pattern",
    "summarize the field notes and tell me the live price of steel",
]

LOCAL_ONLY_TASKS = TASKS[:5]


def main() -> None:
    pipe = LocalAgentPipeline()
    modes: dict = {}
    egress_total = 0
    for i, task in enumerate(TASKS):
        approval = None
        approver = None
        if pipe.model.respond(pipe.redactor.redact(task).text).confidence < pipe.threshold:
            approval = pipe.gate.grant("demo-operator", "act")
            approver = "demo-operator"
        res = pipe.run(
            task,
            approval=approval,
            approver=approver,
            allow_comparison=(i == len(TASKS) - 1),
        )
        modes[res.mode] = modes.get(res.mode, 0) + 1
        egress_total += len(res.egress)
    cost = CostModel().compare(len(TASKS))
    print(f"tasks: {len(TASKS)}")
    print(f"modes: {modes}")
    print(f"egress entries across all runs: {egress_total}")
    print(f"local total for {len(TASKS)} tasks: ${cost['local_total']:.4f}")
    print(f"cloud-pattern total for {len(TASKS)} tasks: ${cost['cloud_total']:.4f}")
    print(f"saving: ${cost['saving']:.4f}")
    print(f"local cheaper: {cost['local_cheaper']}")


if __name__ == "__main__":
    main()
