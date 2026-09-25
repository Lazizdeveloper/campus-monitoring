from campus_monitoring.api.models import (
    ClusterV1DTO,
    ParticipantCampusV1DTO,
    ParticipantProjectV1DTO,
    ParticipantSkillV1DTO,
    ParticipantV1DTO,
    ParticipantWorkstationV1DTO,
    SaleV1DTO,
)
from campus_monitoring.bot.utils.formatter import (
    format_clusters_overview,
    format_participant_profile,
    format_participant_projects,
    format_participant_skills,
    format_sales,
    format_workstation,
)


def test_format_participant_profile() -> None:
    p = ParticipantV1DTO(
        login="test-user",
        className="BOREAS",
        parallelName="Core program",
        expValue=500,
        level=2,
        expToNextLevel=300,
        campus=ParticipantCampusV1DTO(id="123", shortName="Tashkent"),
        status="Active",
    )
    ws = ParticipantWorkstationV1DTO(
        clusterId=1, clusterName="Titan", row="b", number=12
    )
    text = format_participant_profile(p, ws=ws, logtime=4.5)
    assert "test-user" in text
    assert "Titan - B12" in text
    assert "Tashkent" in text
    assert "4.50" in text


def test_format_workstation() -> None:
    ws = ParticipantWorkstationV1DTO(clusterName="Ocean", row="c", number=5)
    text = format_workstation("alex", ws)
    assert "alex" in text
    assert "Ocean" in text
    assert "C5" in text

    offline_text = format_workstation("alex", None)
    assert "Offline" in offline_text


def test_format_clusters_overview() -> None:
    clusters = [
        ClusterV1DTO(id=1, name="Cluster 1", capacity=50, availableCapacity=20, floor=1),
        ClusterV1DTO(id=2, name="Cluster 2", capacity=40, availableCapacity=10, floor=2),
    ]
    text = format_clusters_overview(clusters, campus_name="Tashkent")
    assert "Tashkent" in text
    assert "Cluster 1" in text
    assert "30/50" in text
    assert "Jami o'rinlar: <b>90</b>" in text


def test_format_sales() -> None:
    sales = [
        SaleV1DTO(type="PRP", status="ACTIVE", progressPercentage=50),
    ]
    text = format_sales(sales)
    assert "PRP" in text
    assert "FAOL" in text
    assert "50%" in text
