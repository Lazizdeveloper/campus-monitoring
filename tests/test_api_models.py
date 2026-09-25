import pytest
from campus_monitoring.api.models import (
    CampusV1DTO,
    ClusterMapV1DTO,
    ClusterV1DTO,
    EventV1DTO,
    ParticipantCoalitionV1DTO,
    ParticipantPointsV1DTO,
    ParticipantProjectV1DTO,
    ParticipantSkillV1DTO,
    ParticipantV1DTO,
    ParticipantWorkstationV1DTO,
    SaleV1DTO,
)


def test_participant_v1_dto() -> None:
    data = {
        "login": "bibikov-lukyan",
        "className": "ADONIS",
        "parallelName": "Core program",
        "expValue": 100,
        "level": 0,
        "expToNextLevel": 399,
        "campus": {
            "id": "ff19a3a7-12f5-4332-9582-624519c3eaea",
            "shortName": "Tashkent",
        },
        "status": "Active",
    }
    p = ParticipantV1DTO.model_validate(data)
    assert p.login == "bibikov-lukyan"
    assert p.level == 0
    assert p.campus is not None
    assert p.campus.shortName == "Tashkent"


def test_workstation_dto() -> None:
    data = {
        "clusterId": 854,
        "clusterName": "Ocean",
        "row": "a",
        "number": 24,
    }
    ws = ParticipantWorkstationV1DTO.model_validate(data)
    assert ws.clusterName == "Ocean"
    assert ws.location_str == "Ocean - A24"


def test_cluster_dto() -> None:
    data = {
        "id": 824,
        "name": "Ocean",
        "capacity": 30,
        "availableCapacity": 22,
        "floor": 2,
    }
    cl = ClusterV1DTO.model_validate(data)
    assert cl.capacity == 30
    assert cl.availableCapacity == 22


def test_sale_dto() -> None:
    data = {
        "type": "CRP",
        "status": "ACTIVE",
        "startDateTime": "2024-01-24T11:30:00Z",
        "progressPercentage": 97,
    }
    sale = SaleV1DTO.model_validate(data)
    assert sale.type == "CRP"
    assert sale.status == "ACTIVE"
    assert sale.progressPercentage == 97
