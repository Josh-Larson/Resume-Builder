import dataclasses
import datetime
from typing import Dict, List, Optional


@dataclasses.dataclass
class Author:
	name: str
	title: str
	phone: str
	email: str
	address: str


@dataclasses.dataclass
class ResumeContentBlock:
	title: str
	subtitle: Optional[str] = None
	location: Optional[str] = None
	start_day: Optional[datetime.date] = None
	end_day: Optional[datetime.date] = None
	description: Optional[List[str]] = None


@dataclasses.dataclass
class WorkExperience:
	company: str
	job_title: str
	location: Optional[str]
	start_day: datetime.date
	end_day: Optional[datetime.date]
	description: List[str]

	@property
	def content(self) -> ResumeContentBlock:
		return ResumeContentBlock(self.company, self.job_title, self.location, self.start_day, self.end_day, self.description)


@dataclasses.dataclass
class Certification:
	name: str
	day: datetime.date


@dataclasses.dataclass
class Education:
	school: Optional[str]
	course: Optional[str]
	location: str
	gpa: Optional[float]
	start_day: datetime.date
	end_day: Optional[datetime.date]
	description: List[str]

	@property
	def content(self) -> ResumeContentBlock:
		course = self.course if self.gpa is None else f"{self.course}   [GPA: {self.gpa:.2f}]"
		title = self.school if self.school is not None else course
		subtitle = course if self.school is not None else None
		return ResumeContentBlock(title, subtitle, self.location, self.start_day, self.end_day, self.description)


@dataclasses.dataclass
class Resume:
	author: Author
	pitch: str
	skills: Dict[str, List[str]]
	experience: List[WorkExperience]
	custom_sections: Dict[str, List[ResumeContentBlock]]
	certifications: List[Certification]
	education: List[Education]
	courses: List[Education]
