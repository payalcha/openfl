# Copyright 2020-2023 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
import pytest
import logging

from tests.end_to_end.utils.common_fixtures import fx_local_federated_workflow
from tests.end_to_end.workflow.exclude_flow import TestFlowExclude
from tests.end_to_end.workflow.datastore_cli_flow import TestFlowDatastoreCLI
from tests.end_to_end.workflow.include_exclude_flow import TestFlowIncludeExclude
from tests.end_to_end.workflow.include_flow import TestFlowInclude
from tests.end_to_end.workflow.reference_with_exclude_flow import TestFlowReferenceWithExclude
from tests.end_to_end.workflow.reference_with_include_flow import TestFlowReferenceWithInclude
from tests.end_to_end.workflow.reference_flow import TestFlowReference

log = logging.getLogger(__name__)


def test_exclude_flow(fx_local_federated_workflow):
    flflow = TestFlowExclude(checkpoint=True)
    flflow.runtime = fx_local_federated_workflow.runtime
    try:
        flflow.run()
    except Exception as e:
        log.error(f"Flow failed with exception: {e}")
        raise e


def test_datastore_cli_flow(fx_local_federated_workflow):
    flflow = TestFlowDatastoreCLI(checkpoint=True)
    flflow.runtime = fx_local_federated_workflow.runtime
    try:
        flflow.run()
    except Exception as e:
        log.error(f"Flow failed with exception: {e}")
        raise e


def test_include_exclude_flow(fx_local_federated_workflow):
    flflow = TestFlowIncludeExclude(checkpoint=True)
    flflow.runtime = fx_local_federated_workflow.runtime
    try:
        flflow.run()
    except Exception as e:
        log.error(f"Flow failed with exception: {e}")
        raise e


def test_include_flow(fx_local_federated_workflow):
    flflow = TestFlowInclude(checkpoint=True)
    flflow.runtime = fx_local_federated_workflow.runtime
    try:
        flflow.run()
    except Exception as e:
        log.error(f"Flow failed with exception: {e}")
        raise e


def test_reference_with_exclude_flow(fx_local_federated_workflow):
    flflow = TestFlowReferenceWithExclude(checkpoint=True)
    flflow.runtime = fx_local_federated_workflow.runtime
    try:
        flflow.run()
    except Exception as e:
        log.error(f"Flow failed with exception: {e}")
        raise e


def test_reference_with_include_flow(fx_local_federated_workflow):
    flflow = TestFlowReferenceWithInclude(checkpoint=True)
    flflow.runtime = fx_local_federated_workflow.runtime
    try:
        flflow.run()
    except Exception as e:
        log.error(f"Flow failed with exception: {e}")
        raise e


def test_reference_flow(fx_local_federated_workflow):
    flflow = TestFlowReference(checkpoint=True)
    flflow.runtime = fx_local_federated_workflow.runtime
    try:
        flflow.run()
    except Exception as e:
        log.error(f"Flow failed with exception: {e}")
        raise e
