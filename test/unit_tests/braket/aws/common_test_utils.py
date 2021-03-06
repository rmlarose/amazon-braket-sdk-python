# Copyright 2019-2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import json
from unittest.mock import Mock

DWAVE_ARN = "arn:aws:braket:::device/qpu/d-wave/DW_2000Q_6"
RIGETTI_ARN = "arn:aws:braket:::device/qpu/rigetti/Aspen-8"
IONQ_ARN = "arn:aws:braket:::device/qpu/ionq/ionQdevice"
SIMULATOR_ARN = "arn:aws:braket:::device/quantum-simulator/amazon/sv1"


class MockS3:

    MOCK_S3_RESULT_GATE_MODEL = json.dumps(
        {
            "braketSchemaHeader": {
                "name": "braket.task_result.gate_model_task_result",
                "version": "1",
            },
            "measurements": [[0, 0], [0, 0], [0, 0], [1, 1]],
            "measuredQubits": [0, 1],
            "taskMetadata": {
                "braketSchemaHeader": {"name": "braket.task_result.task_metadata", "version": "1"},
                "id": "task_arn",
                "shots": 100,
                "deviceId": "default",
            },
            "additionalMetadata": {
                "action": {
                    "braketSchemaHeader": {"name": "braket.ir.jaqcd.program", "version": "1"},
                    "instructions": [{"control": 0, "target": 1, "type": "cnot"}],
                },
            },
        }
    )

    MOCK_S3_RESULT_ANNEALING = json.dumps(
        {
            "braketSchemaHeader": {
                "name": "braket.task_result.annealing_task_result",
                "version": "1",
            },
            "solutions": [[-1, -1, -1, -1], [1, -1, 1, 1], [1, -1, -1, 1]],
            "solutionCounts": [3, 2, 4],
            "values": [0.0, 1.0, 2.0],
            "variableCount": 4,
            "taskMetadata": {"id": "task_arn", "shots": 100, "deviceId": DWAVE_ARN,},
            "additionalMetadata": {
                "action": {
                    "type": "ISING",
                    "linear": {"0": 0.3333, "1": -0.333, "4": -0.333, "5": 0.333},
                    "quadratic": {"0,4": 0.667, "0,5": -1.0, "1,4": 0.667, "1,5": 0.667},
                },
                "dwaveMetadata": {
                    "activeVariables": [0],
                    "timing": {
                        "qpuSamplingTime": 100,
                        "qpuAnnealTimePerSample": 20,
                        "qpuAccessTime": 10917,
                        "qpuAccessOverheadTime": 3382,
                        "qpuReadoutTimePerSample": 274,
                        "qpuProgrammingTime": 9342,
                        "qpuDelayTimePerSample": 21,
                        "postProcessingOverheadTime": 117,
                        "totalPostProcessingTime": 117,
                        "totalRealTime": 10917,
                        "runTimeChip": 1575,
                        "annealTimePerRun": 20,
                        "readoutTimePerRun": 274,
                    },
                },
            },
        }
    )


def run_and_assert(
    aws_quantum_task_mock,
    device,
    default_shots,
    default_timeout,
    default_poll_interval,
    circuit,
    s3_destination_folder,
    shots,  # Treated as positional arg
    poll_timeout_seconds,  # Treated as positional arg
    poll_interval_seconds,  # Treated as positional arg
    extra_args,
    extra_kwargs,
):
    task_mock = Mock()
    aws_quantum_task_mock.return_value = task_mock

    run_args = []
    if shots is not None:
        run_args.append(shots)
    if poll_timeout_seconds is not None:
        run_args.append(poll_timeout_seconds)
    if poll_interval_seconds is not None:
        run_args.append(poll_interval_seconds)
    run_args += extra_args if extra_args else []

    run_kwargs = extra_kwargs or {}

    task = device.run(circuit, s3_destination_folder, *run_args, **run_kwargs)
    assert task == task_mock

    create_args = [shots if shots is not None else default_shots]
    create_args += extra_args if extra_args else []

    create_kwargs = extra_kwargs or {}
    create_kwargs.update(
        {
            "poll_timeout_seconds": poll_timeout_seconds
            if poll_timeout_seconds is not None
            else default_timeout,
            "poll_interval_seconds": poll_interval_seconds
            if poll_interval_seconds is not None
            else default_poll_interval,
        }
    )
    aws_quantum_task_mock.assert_called_with(
        device._aws_session,
        device.arn,
        circuit,
        s3_destination_folder,
        *create_args,
        **create_kwargs
    )
