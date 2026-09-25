from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class BaseModelIgnoreExtra(BaseModel):
    model_config = ConfigDict(extra="ignore")


class ErrorResponseDTO(BaseModelIgnoreExtra):
    status: int
    exceptionUUID: Optional[str] = None
    code: str
    message: str


# --- Participant Models ---
class ParticipantCampusV1DTO(BaseModelIgnoreExtra):
    id: str
    shortName: str


class ParticipantV1DTO(BaseModelIgnoreExtra):
    login: str
    className: Optional[str] = None
    parallelName: Optional[str] = None
    expValue: Optional[int] = 0
    level: Optional[int] = 0
    expToNextLevel: Optional[int] = 0
    campus: Optional[ParticipantCampusV1DTO] = None
    status: Optional[str] = None


class ParticipantWorkstationV1DTO(BaseModelIgnoreExtra):
    clusterId: Optional[int] = None
    clusterName: Optional[str] = None
    row: Optional[str] = None
    number: Optional[int] = None

    @property
    def location_str(self) -> str:
        if self.clusterName and self.row and self.number is not None:
            return f"{self.clusterName} - {self.row.upper()}{self.number}"
        return "Noma'lum"


class ParticipantSkillV1DTO(BaseModelIgnoreExtra):
    name: str
    points: int


class ParticipantSkillsV1DTO(BaseModelIgnoreExtra):
    skills: List[ParticipantSkillV1DTO] = Field(default_factory=list)


class ParticipantPointsV1DTO(BaseModelIgnoreExtra):
    peerReviewPoints: Optional[int] = 0
    codeReviewPoints: Optional[int] = 0
    coins: Optional[int] = 0


class TeamMemberV1DTO(BaseModelIgnoreExtra):
    login: str
    isTeamlead: Optional[bool] = False


class ParticipantProjectV1DTO(BaseModelIgnoreExtra):
    id: int
    title: str
    type: Optional[str] = None
    status: str
    finalPercentage: Optional[int] = None
    completionDateTime: Optional[str] = None
    teamMembers: List[TeamMemberV1DTO] = Field(default_factory=list)
    courseId: Optional[int] = None


class ParticipantProjectsV1DTO(BaseModelIgnoreExtra):
    projects: List[ParticipantProjectV1DTO] = Field(default_factory=list)


class ParticipantCoalitionV1DTO(BaseModelIgnoreExtra):
    coalitionId: int
    name: str
    rank: Optional[int] = None


class ParticipantBadgeV1DTO(BaseModelIgnoreExtra):
    name: str
    receiptDateTime: Optional[str] = None
    iconUrl: Optional[str] = None


class ParticipantBadgesV1DTO(BaseModelIgnoreExtra):
    badges: List[ParticipantBadgeV1DTO] = Field(default_factory=list)


class ParticipantXpHistoryItemV1DTO(BaseModelIgnoreExtra):
    expValue: int
    accrualDateTime: Optional[str] = None


class ParticipantXpHistoryV1DTO(BaseModelIgnoreExtra):
    expHistory: List[ParticipantXpHistoryItemV1DTO] = Field(default_factory=list)


class ParticipantLoginsV1DTO(BaseModelIgnoreExtra):
    participants: List[str] = Field(default_factory=list)


# --- Campus & Cluster Models ---
class CampusV1DTO(BaseModelIgnoreExtra):
    id: str
    shortName: str
    fullName: Optional[str] = None


class CampusesV1DTO(BaseModelIgnoreExtra):
    campuses: List[CampusV1DTO] = Field(default_factory=list)


class ClusterV1DTO(BaseModelIgnoreExtra):
    id: int
    name: str
    capacity: int
    availableCapacity: int
    floor: Optional[int] = None


class ClustersV1DTO(BaseModelIgnoreExtra):
    clusters: List[ClusterV1DTO] = Field(default_factory=list)


class WorkplaceV1DTO(BaseModelIgnoreExtra):
    row: str
    number: int
    login: Optional[str] = None


class ClusterMapV1DTO(BaseModelIgnoreExtra):
    clusterMap: List[WorkplaceV1DTO] = Field(default_factory=list)


class CoalitionV1DTO(BaseModelIgnoreExtra):
    coalitionId: int
    name: str


class CoalitionsV1DTO(BaseModelIgnoreExtra):
    coalitions: List[CoalitionV1DTO] = Field(default_factory=list)


# --- Events & Sales Models ---
class EventV1DTO(BaseModelIgnoreExtra):
    id: int
    type: Optional[str] = None
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    startDateTime: Optional[str] = None
    endDateTime: Optional[str] = None
    organizers: Optional[List[str]] = Field(default_factory=list)
    capacity: Optional[int] = None
    registerCount: Optional[int] = None


class EventsV1DTO(BaseModelIgnoreExtra):
    events: List[EventV1DTO] = Field(default_factory=list)


class SaleV1DTO(BaseModelIgnoreExtra):
    type: str  # PRP or CRP
    status: str  # NON_ACTIVE, ACTIVE, PLANNED
    startDateTime: Optional[str] = None
    progressPercentage: Optional[int] = None


class SalesV1DTO(BaseModelIgnoreExtra):
    sales: List[SaleV1DTO] = Field(default_factory=list)


# --- Project Info ---
class ProjectV1DTO(BaseModelIgnoreExtra):
    id: int
    title: Optional[str] = None
    description: Optional[str] = None
