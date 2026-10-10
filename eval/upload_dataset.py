"""One-off script: push CASES from eval/datasets/mira_baseline.py into a
LangSmith dataset. Re-running it updates examples in place (matched by id).

    python -m eval.upload_dataset
"""

import keystore.setenv  # noqa: F401  (loads env vars before anything else)

from eval.datasets.mira_baseline import CASES
from observability.client import get_client

DATASET_NAME = "mira-baseline"


def main() -> None:
    client = get_client()

    if not client.has_dataset(dataset_name=DATASET_NAME):
        client.create_dataset(
            dataset_name=DATASET_NAME,
            description="Baseline capability checks for the MIRA pipeline (T1-T12).",
        )

    dataset = client.read_dataset(dataset_name=DATASET_NAME)

    existing = {
        example.metadata.get("id"): example
        for example in client.list_examples(dataset_id=dataset.id)
        if example.metadata
    }

    for case in CASES:
        inputs = {"query": case["query"], "vague": case["vague"]}
        outputs = {
            "must_contain": case["must_contain"],
            "expected_intents": case["expected_intents"],
            "expect": case["expect"],
        }
        metadata = {"id": case["id"]}

        if case["id"] in existing:
            client.update_example(
                example_id=existing[case["id"]].id,
                inputs=inputs,
                outputs=outputs,
                metadata=metadata,
            )
        else:
            client.create_example(
                dataset_id=dataset.id,
                inputs=inputs,
                outputs=outputs,
                metadata=metadata,
            )

    print(f"Uploaded {len(CASES)} examples to dataset '{DATASET_NAME}'.")


if __name__ == "__main__":
    main()
