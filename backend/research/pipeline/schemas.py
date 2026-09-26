from pydantic import BaseModel, Field


class Trend(BaseModel):
    title: str
    why_now: str
    source_ids: list[int] = Field(min_length=1)


class LearnItem(BaseModel):
    skill: str
    why: str
    source_ids: list[int] = Field(min_length=1)


class RoadmapWeek(BaseModel):
    week: int
    goal: str
    tasks: list[str] = Field(min_length=1, max_length=5)
    resource_ids: list[int]


class Report(BaseModel):
    trends: list[Trend] = Field(min_length=3, max_length=6)
    learn: list[LearnItem] = Field(min_length=3, max_length=5)
    roadmap: list[RoadmapWeek] = Field(min_length=3, max_length=4)
