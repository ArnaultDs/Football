from pydantic import BaseModel, Field, TypeAdapter, ConfigDict, computed_field
from typing import Literal, Union, Annotated, Any

import pendulum

def get_current_time_str() -> str: 

    now = pendulum.now(tz="Europe/Paris")
    return now.strftime("%Y%m%d%H%M%S")

class InterfaceBase(BaseModel): 
    model_config = ConfigDict(extra="forbid")

    page: int = Field(default=1, exclude=True)

    @property
    def params(self) -> dict[str, Any]: 
        return self.model_dump(exclude_none=True)

    @property
    def file_name(self) -> str: 
        return f"extracted-{get_current_time_str()}_p{str(self.page).zfill(4)}"

class LeagueInterface(InterfaceBase): 

    endpoint: Literal["leagues"] = Field(default="leagues", exclude=True)

    league: int | None = Field(default=None, exclude=True)
    season: int

    @computed_field
    @property
    def id(self) -> int | None: 
        return self.league

    @property
    def partitions(self) -> str: 

        league = self.league or "all"

        return f"{self.endpoint}/league={league}/season={self.season}"
    

class FixtureInterface(InterfaceBase): 

    endpoint: Literal["fixtures"] = Field(default="fixtures", exclude=True)

    id: str | None = Field(default=None)
    league: int
    season: int
    date: str | None = Field(default=None)

    @property
    def partitions(self) -> str: 
        return f"{self.endpoint}/league={self.league}/season={self.season}"

class RoundInterface(InterfaceBase):

    endpoint: Literal["fixtures/rounds"] = Field(default="fixtures/rounds", exclude=True)

    league: int
    season: int

    @property
    def partitions(self) -> str: 
        return f"{self.endpoint}/league={self.league}/season={self.season}"

    

class TeamInterface(InterfaceBase): 
    endpoint: Literal["teams"] = Field(default="teams", exclude=True)
    
    id: str | None = Field(default=None)
    league: int
    season: int

    @property
    def partitions(self) -> str: 
        return f"{self.endpoint}/league={self.league}/season={self.season}"

    @property
    def file_name(self) -> str: 
        return f"{self.endpoint}_p{str(self.page).zfill(4)}"

class FixtureStatisticsInterface(InterfaceBase):
    endpoint: Literal["fixtures/players"] = Field(default="fixtures/players", exclude=True)

    fixture: int
    league: int = Field(exclude=True)
    season: int = Field(exclude=True)

    @property
    def partitions(self) -> str: 
        return f"{self.endpoint}/league={self.league}/season={self.season}"


ApiInterface = Annotated[
    Union[LeagueInterface, FixtureInterface, TeamInterface, FixtureStatisticsInterface, RoundInterface],
    Field(discriminator="endpoint")
]

api_interface: TypeAdapter[ApiInterface] = TypeAdapter(ApiInterface)
