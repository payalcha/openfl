# Copyright (C) 2020-2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import sys
import logging
from openfl.experimental.workflow.interface import FLSpec, Aggregator, Collaborator
from openfl.experimental.workflow.runtime import LocalRuntime
from openfl.experimental.workflow.placement import aggregator, collaborator

log = logging.getLogger(__name__)

class TestFlowInclude(FLSpec):
    """
    Testflow to validate include functionality in Federated Flow
    """

    include_error_list = []

    @aggregator
    def start(self):
        """
        Flow start.
        """
        log.info("Testing FederatedFlow - Starting Test for Include Attributes")
        self.collaborators = self.runtime.collaborators

        self.exclude_agg_to_agg = 10
        self.include_agg_to_agg = 100
        self.next(
            self.test_include_agg_to_agg,
            include=["include_agg_to_agg", "collaborators"],
        )

    @aggregator
    def test_include_agg_to_agg(self):
        """
        Testing whether attributes are included from agg to agg
        """
        if (
            hasattr(self, "include_agg_to_agg") is True
            and hasattr(self, "exclude_agg_to_agg") is False
        ):
            log.info("... Include test passed in test_include_agg_to_agg")
        else:
            TestFlowInclude.include_error_list.append("test_include_agg_to_agg")
            log.error("... Include test failed in test_include_agg_to_agg")

        self.include_agg_to_collab = 100
        self.exclude_agg_to_collab = 78
        self.next(
            self.test_include_agg_to_collab,
            foreach="collaborators",
            include=["include_agg_to_collab", "collaborators"],
        )

    @collaborator
    def test_include_agg_to_collab(self):
        """
        Testing whether attributes are included from agg to collab
        """
        if (
            hasattr(self, "include_agg_to_agg") is False
            and hasattr(self, "exclude_agg_to_agg") is False
            and hasattr(self, "exclude_agg_to_collab") is False
            and hasattr(self, "include_agg_to_collab") is True
        ):
            log.info("... Include test passed in test_include_agg_to_collab")
        else:
            TestFlowInclude.include_error_list.append("test_include_agg_to_collab")
            log.error("... Include test failed in test_include_agg_to_collab")
        self.exclude_collab_to_collab = 10
        self.include_collab_to_collab = 44
        self.next(
            self.test_include_collab_to_collab,
            include=["include_collab_to_collab"],
        )

    @collaborator
    def test_include_collab_to_collab(self):
        """
        Testing whether attributes are included from collab to collab
        """
        if (
            hasattr(self, "include_agg_to_agg") is False
            and hasattr(self, "include_agg_to_collab") is False
            and hasattr(self, "include_collab_to_collab") is True
            and hasattr(self, "exclude_agg_to_agg") is False
            and hasattr(self, "exclude_agg_to_collab") is False
            and hasattr(self, "exclude_collab_to_collab") is False
        ):
            log.info("... Include test passed in test_include_collab_to_collab")
        else:
            TestFlowInclude.include_error_list.append("test_include_collab_to_collab")
            log.error("... Include test failed in test_include_collab_to_collab")

        self.exclude_collab_to_agg = 20
        self.include_collab_to_agg = 56
        self.next(self.join, include=["include_collab_to_agg"])

    @aggregator
    def join(self, inputs):
        """
        Testing whether attributes are included from collab to agg
        """
        # Aggregator attribute check
        validate = (
            hasattr(self, "include_agg_to_agg") is True
            and hasattr(self, "include_agg_to_collab") is True
            and hasattr(self, "exclude_agg_to_collab") is True
            and hasattr(self, "exclude_agg_to_agg") is False
        )

        # Collaborator attribute check
        for input in inputs:
            validation = validate and (
                hasattr(input, "include_collab_to_collab") is False
                and hasattr(input, "exclude_collab_to_collab") is False
                and hasattr(input, "exclude_collab_to_agg") is False
                and hasattr(input, "include_collab_to_agg") is True
            )

        if validation:
            log.info("... Include test passed in join")
        else:
            TestFlowInclude.include_error_list.append("join")
            log.error("... Include test failed in join")

        log.info("Include attribute test summary:")

        if TestFlowInclude.include_error_list:
            validated_include_variables = ",".join(TestFlowInclude.include_error_list)
            log.error(f"...Test case failed for {validated_include_variables}")

        self.next(self.end)

    @aggregator
    def end(self):
        """
        This is the 'end' step. All flows must have an 'end' step, which is the
        last step in the flow.
        """
        log.info("Testing FederatedFlow - Ending Test for Include Attributes")
        if TestFlowInclude.include_error_list:
            raise (
                AssertionError(
                    "\n ...Test case failed ..."
                )
            )


if __name__ == "__main__":
    # Setup participants
    aggregator = Aggregator()

    # Setup collaborators
    collaborator_names = ["Portland", "Chandler", "Bangalore", "Delhi"]
    collaborators = []
    for collaborator_name in collaborator_names:
        collaborators.append(Collaborator(name=collaborator_name))

    local_runtime = LocalRuntime(
        aggregator=aggregator,
        collaborators=collaborators,
    )

    if len(sys.argv) > 1:
        if sys.argv[1] == "ray":
            local_runtime = LocalRuntime(
                aggregator=aggregator, collaborators=collaborators, backend="ray"
            )

    log.info(f"Local runtime collaborators = {local_runtime.collaborators}")

    flflow = TestFlowInclude(checkpoint=True)
    flflow.runtime = local_runtime
    for i in range(5):
        log.info(f"Starting round {i}...")
        flflow.run()

    log.info("End of Testing FederatedFlow")
