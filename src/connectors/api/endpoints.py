from pydantic import BaseModel, Field, TypeAdapter, ConfigDict, computed_field
from typing import Literal, Union, Annotated, Any

import pendulum

def get_current_time_str() -> str: 

    now = pendulum.now(tz="Europe/Paris")
    return now.strftime("%Y%m%d%H%M%S")

class EndpointParams(BaseModel): 
    model_config = ConfigDict(extra="forbid")

    page: int = Field(default=1, exclude=True)

    @property
    def query_params(self) -> dict[str, Any]: 
        return self.model_dump(exclude_none=True)

    @property
    def file_name(self) -> str: 
        return f"extracted-{get_current_time_str()}_p{str(self.page).zfill(4)}"

class LeagueParams(EndpointParams): 

    endpoint: Literal["leagues"] = Field(default="leagues", exclude=True)

    league: int | None = Field(default=None, exclude=True)
    season: int

    @computed_field
    @property
    def id(self) -> int | None: 
        return self.league

    @property
    def partition_path(self) -> str: 

        league = self.league or "all"

        return f"{self.endpoint}/league={league}/season={self.season}"
    

class FixtureParams(EndpointParams): 

    endpoint: Literal["fixtures"] = Field(default="fixtures", exclude=True)

    id: str | None = Field(default=None)
    league: int
    season: int
    date: str | None = Field(default=None)

    @property
    def partition_path(self) -> str: 
        return f"{self.endpoint}/league={self.league}/season={self.season}"

class RoundParams(EndpointParams):

    endpoint: Literal["fixtures/rounds"] = Field(default="fixtures/rounds", exclude=True)

    league: int
    season: int

    @property
    def partition_path(self) -> str: 
        return f"{self.endpoint}/league={self.league}/season={self.season}"

    

class TeamParams(EndpointParams): 
    endpoint: Literal["teams"] = Field(default="teams", exclude=True)
    
    id: str | None = Field(default=None)
    league: int
    season: int

    @property
    def partition_path(self) -> str: 
        return f"{self.endpoint}/league={self.league}/season={self.season}"

class FixtureStatisticsParams(EndpointParams):
    endpoint: Literal["fixtures/players"] = Field(default="fixtures/players", exclude=True)

    fixture: int
    league: int = Field(exclude=True)
    season: int = Field(exclude=True)

    @property
    def partition_path(self) -> str: 
        return f"{self.endpoint}/league={self.league}/season={self.season}"
    
    @property
    def file_name(self) -> str:
        return f"fixture-{self.fixture}_extracted-{get_current_time_str()}_p{str(self.page).zfill(4)}"


AnyEndpointParams = Annotated[
    Union[LeagueParams, FixtureParams, TeamParams, FixtureStatisticsParams, RoundParams],
    Field(discriminator="endpoint")
]

endpoint_params_adapter: TypeAdapter[AnyEndpointParams] = TypeAdapter(AnyEndpointParams)
