from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional
import aiohttp

from campus_monitoring.api.exceptions import (
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    School21ApiError,
    ServerError,
    UnauthorizedError,
)
from campus_monitoring.api.models import (
    CampusesV1DTO,
    ClusterMapV1DTO,
    ClustersV1DTO,
    CoalitionsV1DTO,
    EventsV1DTO,
    ParticipantBadgesV1DTO,
    ParticipantCoalitionV1DTO,
    ParticipantLoginsV1DTO,
    ParticipantPointsV1DTO,
    ParticipantProjectsV1DTO,
    ParticipantSkillsV1DTO,
    ParticipantV1DTO,
    ParticipantWorkstationV1DTO,
    ParticipantXpHistoryV1DTO,
    ProjectV1DTO,
    SalesV1DTO,
)

logger = logging.getLogger(__name__)


class School21ApiClient:
    def __init__(self, base_url: str, token: str, auth_callback=None):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.auth_callback = auth_callback
        self._session: Optional[aiohttp.ClientSession] = None

    def _get_headers(self) -> Dict[str, str]:
        auth_header = self.token
        if auth_header and not auth_header.startswith("Bearer "):
            auth_header = f"Bearer {auth_header}"
        return {
            "Authorization": auth_header,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(ssl=False)
            self._session = aiohttp.ClientSession(
                headers=self._get_headers(),
                timeout=aiohttp.ClientTimeout(total=15),
                connector=connector,
            )
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        session = await self.get_session()
        url = f"{self.base_url}{endpoint}"
        
        cleaned_params = {}
        if params:
            for k, v in params.items():
                if v is not None:
                    if isinstance(v, bool):
                        cleaned_params[k] = str(v).lower()
                    else:
                        cleaned_params[k] = v

        try:
            # API xatosi tufayli login pageda (keycloak:8080) xato yuz bermasligi uchun 
            # allow_redirects=False qilib qo'yamiz
            async with session.request(method, url, params=cleaned_params, allow_redirects=False) as resp:
                if resp.status == 200:
                    return await resp.json()

                error_data = {}
                try:
                    error_data = await resp.json()
                except Exception:
                    pass

                message = error_data.get("message", resp.reason or "Xatolik yuz berdi")
                uuid = error_data.get("exceptionUUID", "")
                code = error_data.get("code", "")

                if resp.status in (401, 302, 303):
                    # Token muddati tugagan bo'lishi mumkin, uni yangilaymiz
                    if self.auth_callback:
                        logger.info(f"{resp.status} status qabul qilindi. Tokenni avtomatik yangilash jarayoni boshlandi...")
                        try:
                            new_token = await self.auth_callback()
                            if new_token:
                                self.token = new_token
                                # Retry the request with the new token
                                if self._session and not self._session.closed:
                                    self._session.headers.update(self._get_headers())
                                async with self._session.request(method, url, params=cleaned_params, allow_redirects=False) as retry_resp:
                                    if retry_resp.status == 200:
                                        return await retry_resp.json()
                        except Exception as auth_e:
                            logger.error(f"Tokenni yangilashda xatolik: {auth_e}")
                    raise UnauthorizedError(message=f"Avtorizatsiya xatosi (status: {resp.status})", uuid=uuid)
                elif resp.status == 403:
                    raise ForbiddenError(message=message, uuid=uuid)
                elif resp.status == 404:
                    raise NotFoundError(message=message, uuid=uuid)
                elif resp.status == 429:
                    raise RateLimitError(message=message, uuid=uuid)
                elif resp.status >= 500:
                    raise ServerError(message=message, uuid=uuid)
                else:
                    raise School21ApiError(message=message, status_code=resp.status, code=code, uuid=uuid)
        except aiohttp.ClientError as e:
            logger.error(f"Network error while requesting {url}: {e}")
            raise School21ApiError(message=f"Tarmoq xatosi: {e}", status_code=0)

    # --- Participant Methods ---
    async def get_participant(self, login: str) -> ParticipantV1DTO:
        data = await self._request("GET", f"/v1/participants/{login.strip()}")
        return ParticipantV1DTO.model_validate(data)

    async def get_participant_workstation(self, login: str) -> Optional[ParticipantWorkstationV1DTO]:
        try:
            data = await self._request("GET", f"/v1/participants/{login.strip()}/workstation")
            return ParticipantWorkstationV1DTO.model_validate(data)
        except NotFoundError:
            return None

    async def get_participant_skills(self, login: str) -> ParticipantSkillsV1DTO:
        data = await self._request("GET", f"/v1/participants/{login.strip()}/skills")
        return ParticipantSkillsV1DTO.model_validate(data)

    async def get_participant_points(self, login: str) -> ParticipantPointsV1DTO:
        data = await self._request("GET", f"/v1/participants/{login.strip()}/points")
        return ParticipantPointsV1DTO.model_validate(data)

    async def get_participant_projects(
        self,
        login: str,
        status: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> ParticipantProjectsV1DTO:
        params = {"status": status, "limit": limit, "offset": offset}
        data = await self._request("GET", f"/v1/participants/{login.strip()}/projects", params=params)
        return ParticipantProjectsV1DTO.model_validate(data)

    async def get_participant_logtime(self, login: str, date: Optional[str] = None) -> float:
        params = {"date": date}
        data = await self._request("GET", f"/v1/participants/{login.strip()}/logtime", params=params)
        return float(data) if isinstance(data, (int, float)) else 0.0

    async def get_participant_coalition(self, login: str) -> Optional[ParticipantCoalitionV1DTO]:
        try:
            data = await self._request("GET", f"/v1/participants/{login.strip()}/coalition")
            return ParticipantCoalitionV1DTO.model_validate(data)
        except NotFoundError:
            return None

    async def get_participant_badges(self, login: str) -> ParticipantBadgesV1DTO:
        data = await self._request("GET", f"/v1/participants/{login.strip()}/badges")
        return ParticipantBadgesV1DTO.model_validate(data)

    async def get_participant_xp_history(
        self, login: str, limit: int = 20, offset: int = 0
    ) -> ParticipantXpHistoryV1DTO:
        params = {"limit": limit, "offset": offset}
        data = await self._request("GET", f"/v1/participants/{login.strip()}/experience-history", params=params)
        return ParticipantXpHistoryV1DTO.model_validate(data)

    # --- Campus & Cluster Methods ---
    async def get_campuses(self) -> CampusesV1DTO:
        data = await self._request("GET", "/v1/campuses")
        return CampusesV1DTO.model_validate(data)

    async def get_campus_clusters(self, campus_id: str) -> ClustersV1DTO:
        data = await self._request("GET", f"/v1/campuses/{campus_id}/clusters")
        return ClustersV1DTO.model_validate(data)

    async def get_campus_coalitions(
        self, campus_id: str, limit: int = 50, offset: int = 0
    ) -> CoalitionsV1DTO:
        params = {"limit": limit, "offset": offset}
        data = await self._request("GET", f"/v1/campuses/{campus_id}/coalitions", params=params)
        return CoalitionsV1DTO.model_validate(data)

    async def get_cluster_map(
        self,
        cluster_id: int,
        occupied: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> ClusterMapV1DTO:
        params = {"occupied": occupied, "limit": limit, "offset": offset}
        data = await self._request("GET", f"/v1/clusters/{cluster_id}/map", params=params)
        return ClusterMapV1DTO.model_validate(data)

    # --- Sales & Events ---
    async def get_sales(self) -> SalesV1DTO:
        data = await self._request("GET", "/v1/sales")
        return SalesV1DTO.model_validate(data)

    async def get_events(
        self,
        from_date: str,
        to_date: str,
        event_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> EventsV1DTO:
        params = {
            "from": from_date,
            "to": to_date,
            "type": event_type,
            "limit": limit,
            "offset": offset,
        }
        data = await self._request("GET", "/v1/events", params=params)
        return EventsV1DTO.model_validate(data)

    async def get_project(self, project_id: int) -> ProjectV1DTO:
        data = await self._request("GET", f"/v1/projects/{project_id}")
        return ProjectV1DTO.model_validate(data)
