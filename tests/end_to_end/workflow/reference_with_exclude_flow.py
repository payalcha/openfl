import logging

from openfl.experimental.workflow.interface import FLSpec, Aggregator, Collaborator
from openfl.experimental.workflow.runtime import LocalRuntime
from openfl.experimental.workflow.placement import aggregator, collaborator

import sys
import torch.nn as nn
import torch.optim as optim
import inspect
from types import MethodType


MIN_COLLECTION_COUNT = 2

log = logging.getLogger(__name__)


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.linear1 = nn.Linear(60, 100)
        self.linear2 = nn.Linear(100, 10)

    def forward(self, x):
        x = self.linear1(x)
        x = self.linear2(x)
        return x


class TestFlowReferenceWithExclude(FLSpec):

    """
    Testflow to validate references of collabartor attributes in Federated Flow with exclude.

    """

    step_one_collab_attrs = []
    step_two_collab_attrs = []
    all_ref_error_dict = {}

    @aggregator
    def start(self):
        """
        Flow start.

        """
        self.agg_agg_attr_dict = {key: key for key in range(5)}
        log.info("Testing FederatedFlow - Starting Test for validating references")
        self.next(self.test_create_agg_attr, exclude=["agg_agg_attr_dict"])

    @aggregator
    def test_create_agg_attr(self):
        """
        Create different types of objects
        """

        self.agg_attr_list = [1, 2, 5, 6, 7, 8]
        self.agg_attr_dict = {key: key for key in range(5)}
        self.agg_attr_model = Net()
        self.agg_attr_optimizer = optim.SGD(
            self.agg_attr_model.parameters(), lr=1e-3, momentum=1e-2
        )
        self.collaborators = self.runtime.collaborators

        self.next(
            self.test_create_collab_attr,
            foreach="collaborators",
            exclude=["agg_attr_list"],
        )

    @collaborator
    def test_create_collab_attr(self):
        """
        Create different types of objects
        """
        self.collab_attr_list_one = [1, 2, 3, 5, 6, 8]
        self.collab_attr_dict_one = {key: key for key in range(5)}

        TestFlowReferenceWithExclude.step_one_collab_attrs.append(self)

        if (
            len(TestFlowReferenceWithExclude.step_one_collab_attrs)
            >= MIN_COLLECTION_COUNT
        ):
            collab_attr_list = filter_attrs(inspect.getmembers(self))
            matched_ref_dict = find_matched_references(
                collab_attr_list,
                TestFlowReferenceWithExclude.step_one_collab_attrs,
            )
            validate_references(matched_ref_dict)

        self.next(self.test_create_more_collab_attr, exclude=["collab_attr_dict_one"])

    @collaborator
    def test_create_more_collab_attr(self):
        """
        Create different types of objects
        """
        self.collab_attr_list_two = [1, 2, 3, 5, 6, 8]
        self.collab_attr_dict_two = {key: key for key in range(5)}

        TestFlowReferenceWithExclude.step_two_collab_attrs.append(self)

        if (
            len(TestFlowReferenceWithExclude.step_two_collab_attrs)
            >= MIN_COLLECTION_COUNT
        ):
            collab_attr_list = filter_attrs(inspect.getmembers(self))
            matched_ref_dict = find_matched_references(
                collab_attr_list,
                TestFlowReferenceWithExclude.step_two_collab_attrs,
            )
            validate_references(matched_ref_dict)

        self.next(self.join, exclude=["collab_attr_dict_two"])

    @aggregator
    def join(self, inputs):
        """
        Iterate over the references of collaborator attributes
        validate uniqueness of attributes and raise assertion
        """

        all_attr_list = filter_attrs(inspect.getmembers(inputs[0]))

        matched_ref_dict = find_matched_references(all_attr_list, inputs)
        validate_references(matched_ref_dict)

        all_shared_attr = ""
        log.info("Reference with exclude keyword test summary:")

        for val in TestFlowReferenceWithExclude.all_ref_error_dict.values():
            all_shared_attr = all_shared_attr + ",".join(val)

        if all_shared_attr:
            log.error(f"Test case failed for {all_shared_attr}")
        else:
            log.info("Test case passed for all the attributes.")
        self.next(self.end)

    @aggregator
    def end(self):
        log.info("Testing FederatedFlow - Ending test for validatng the references.")

        if TestFlowReferenceWithExclude.all_ref_error_dict:
            raise (
                AssertionError(
                    "Test case failed"
                )
            )

        TestFlowReferenceWithExclude.step_one_collab_attrs = []
        TestFlowReferenceWithExclude.step_two_collab_attrs = []
        TestFlowReferenceWithExclude.all_ref_error_dict = {}


def filter_attrs(attr_list):
    valid_attrs = []
    reserved_words = ["next", "runtime", "execute_next"]
    for attr in attr_list:
        if (
            not attr[0].startswith("_")
            and attr[0] not in reserved_words
            and not hasattr(TestFlowReferenceWithExclude, attr[0])
        ):
            if not isinstance(attr[1], MethodType):
                valid_attrs.append(attr[0])
    return valid_attrs


def find_matched_references(collab_attr_list, all_collaborators):
    """
    Iterate attributes of collborator and capture the duplicate reference
    return: dict: {
                    'Portland': ['failed attributes'], 'Seattle': [],
                  }
    """
    matched_ref_dict = {}
    for i in range(len(all_collaborators)):
        matched_ref_dict[all_collaborators[i].input] = []

    # For each attribute in the collaborator attribute list, check if any of the collaborator
    # attributes are shared with another collaborator
    for attr_name in collab_attr_list:
        for i, curr_collab in enumerate(all_collaborators):
            # Compare the current collaborator with the collaborator(s) that come(s) after it.
            for next_collab in all_collaborators[i + 1:]:
                # Check if both collaborators have the current attribute
                if hasattr(curr_collab, attr_name) and hasattr(next_collab, attr_name):
                    # Check if both collaborators are sharing same reference
                    if getattr(curr_collab, attr_name) is getattr(
                        next_collab, attr_name
                    ):
                        matched_ref_dict[curr_collab.input].append(attr_name)
                        log.error(
                            f"Reference test failed - {curr_collab.input} sharing same "
                            + f"{attr_name} reference with {next_collab.input}"
                        )

    return matched_ref_dict


def validate_references(matched_ref_dict):
    """
    Iterate reference list and raise assertion for conflicts
    """
    collborators_sharing_ref = []
    reference_flag = False

    for collab, val in matched_ref_dict.items():
        if val:
            collborators_sharing_ref.append(collab)
            reference_flag = True
    if collborators_sharing_ref:
        for collab in collborators_sharing_ref:
            if collab not in TestFlowReferenceWithExclude.all_ref_error_dict:
                TestFlowReferenceWithExclude.all_ref_error_dict[
                    collab
                ] = matched_ref_dict.get(collab)

    if not reference_flag:
        log.info("Pass : Reference test passed")


if __name__ == "__main__":
    # Setup participants
    aggregator = Aggregator()

    # Setup collaborators
    collaborator_names = ["Portland", "Seattle", "Chandler", "Bangalore"]
    collaborators = []
    for idx, collaborator_name in enumerate(collaborator_names):
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

    testflow = TestFlowReferenceWithExclude(checkpoint=True)
    testflow.runtime = local_runtime

    for i in range(5):
        log.info(f"Starting round {i}...")
        testflow.run()
