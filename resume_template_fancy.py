import pathlib
import re
from typing import List, Tuple

from data import Education, Resume, ResumeContentBlock
from resume_generator import ResumeGenerator

from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class TemporaryMarginIncrease:
	def __init__(self, resume: ResumeGenerator, increase: float, has_right_margin: bool = True):
		self.resume = resume
		self.increase = increase
		self.margin_before = self.resume.margin
		self.page_size_before = self.resume.page_size
		self.has_right_margin = has_right_margin

	def __enter__(self):
		page_size_increase = self.increase * (1 if self.has_right_margin else 2)
		self.resume.margin = self.margin_before[0] + self.increase, self.margin_before[1]
		self.resume.page_size = self.page_size_before[0] + page_size_increase, self.page_size_before[1]
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.resume.margin = self.margin_before
		self.resume.page_size = self.page_size_before
		return False


class ResumeTemplateFancy(ResumeGenerator):
	def __init__(self, resume: Resume, output_path: str):
		super().__init__(resume, output_path)
		self.text_color = HexColor(0x000000)
		self.left_bar_color = HexColor(0xFFBD88)
		self.left_bar_text_color = HexColor(0x000000)
		self.left_bar_width = 3.4 * 72
		self.left_bar_drawable_width = self.left_bar_width - 0.15 * 72

		self.experience_continuity_color = HexColor(0x888FFF)
		self.full_page_size = self.page_size

	def _set_symbola(self):
		self.canvas.setFont("Symbola", 12)
		self.font = None

	def _draw_left_bar_section_header(self, title: str):
		self.canvas.line(self.margin[0], self.pos - 3, self.left_bar_drawable_width, self.pos - 3)
		self._draw_left(title, height=14, bold=True)
		self.pos -= 3

	def _draw_left_bar_contact(self):
		self._draw_left_bar_section_header("Contact")
		author = self.resume.author
		height = 18 + 14 * 4
		if height > self.pos - self.margin[1]:
			self._new_page()
		phone = re.sub("[^0-9]", "", author.phone)
		with TemporaryMarginIncrease(self, 7):
			emoji_x = self.margin[0]
			with TemporaryMarginIncrease(self, 20):
				self._set_symbola()
				self.canvas.drawString(emoji_x, self.pos, "\U0001F4DE")
				self._draw_left(f"({phone[:3]}) {phone[3:6]}-{phone[6:]}")
				self._set_symbola()
				self.canvas.drawString(emoji_x, self.pos, "\U0001F582")
				self._draw_left(author.email)
				self._set_symbola()
				self.canvas.drawString(emoji_x, self.pos, "\U0001F4CD")
				self._draw_left(author.address)

	def _draw_left_bar_skills(self):
		self._draw_left_bar_section_header("Skills")
		with TemporaryMarginIncrease(self, 7):
			for idx, (skill_title, skill_list) in enumerate(self.resume.skills.items()):
				self._draw_left(skill_title, height=12, bold=True)
				self.pos -= 4
				self._draw_left(", ".join(skill_list))
				if idx + 1 < len(self.resume.skills):
					self._draw_left("")

	def _draw_left_bar_education(self):
		self._draw_left_bar_section_header("Education")
		with TemporaryMarginIncrease(self, 7):
			for idx, education in enumerate(self.resume.education):
				self._draw_left(education.course, height=12, bold=True)
				self._draw_left(education.school, height=12)
				self._draw_left(education.location, height=12)
				self._draw_left(
					f"{education.start_day.strftime('%b %Y')} - {education.end_day.strftime('%b %Y') if education.end_day else 'Present'}")
				self._draw_left(f"GPA: {education.gpa}")
				if idx + 1 < len(self.resume.education):
					self._draw_left("")

	def _draw_left_bar(self):
		self.canvas.setFillColor(self.left_bar_color)
		self.canvas.rect(0, 0, self.left_bar_width, self.page_size[1], stroke=0, fill=1)
		self.canvas.setFillColor(self.left_bar_text_color)
		tmp_size_save = self.page_size
		self.page_size = (self.left_bar_drawable_width + self.margin[0], tmp_size_save[1])

		# Name / Title
		self.pos -= 22
		self._draw_left(self.resume.author.name, height=22, bold=True)
		self._draw_left(self.resume.author.title, height=14)
		self._draw_left("", height=8)
		self._draw_left(self.resume.pitch)
		self._draw_left("")

		# Sections
		self._draw_left_bar_contact()
		self._draw_left("")
		self._draw_left_bar_education()
		self._draw_left("")
		self._draw_left_bar_skills()

		self.page_size = tmp_size_save

	def _draw_right_bar_section_header(self, title: str):
		self.canvas.line(self.margin[0], self.pos - 3, self.full_page_size[0], self.pos - 3)
		self._draw_left(title, height=16, bold=True)
		self.pos -= 3

	def draw_custom_section(self, section_name: str):
		section_contents = self.resume.custom_sections[section_name]
		self._draw_right_bar_section_header(section_name)
		for idx, section in enumerate(section_contents):
			self._draw_resume_content_block(section)
			if idx + 1 < len(self.resume.custom_sections):
				self._draw_left("")

	def draw_work_experience(self):
		experience = self.resume.experience
		if len(experience) == 0:
			return
		height = 18 + self._get_resume_content_block_height(experience[0].content)
		if height > self.pos - self.margin[1]:
			self._new_page()
		self._draw_right_bar_section_header("WORK EXPERIENCE")
		experience_run_length = []
		for exp in experience:
			if len(experience_run_length) == 0 or experience_run_length[-1]["company"] != exp.company:
				experience_run_length.append({"company": exp.company, "experience": [exp]})
			else:
				experience_run_length[-1]["experience"].append(exp)
		for exp_run_length in experience_run_length:
			start_y = self.pos
			self.canvas.setStrokeColor(self.experience_continuity_color)
			self.canvas.circle(self.margin[0], self.pos + 4, 4, stroke=1, fill=0)
			self.canvas.setStrokeColor(self.text_color)
			with TemporaryMarginIncrease(self, 7):
				self._draw_left(exp_run_length["company"], height=14, bold=True, underline=True)
				with TemporaryMarginIncrease(self, 7):
					for idx, exp in enumerate(exp_run_length["experience"]):
						prev_pos = self.pos
						self._draw_left(exp.job_title, bold=True)
						self.pos = prev_pos
						self._draw_right(f"{exp.start_day.strftime('%b %Y')} - {exp.end_day.strftime('%b %Y') if exp.end_day else 'Present'}")
						self._draw_left(exp.location)
						for bullet in exp.description:
							if bullet.startswith("\t"):
								tabs = len(bullet) - len(bullet.lstrip("\t"))
								bullet = bullet.lstrip("\t")
								self._draw_left(f"{'    ' * tabs} \u2022 {bullet}")
							else:
								self._draw_left(f" \u2022 {bullet}")
						self._draw_left("")
			self.canvas.setStrokeColor(self.experience_continuity_color)
			self.canvas.line(self.margin[0], start_y, self.margin[0], self.pos + 24)
			self.canvas.setStrokeColor(self.text_color)

	def _draw_right_bar(self, sections: list):
		self.pos = self.page_size[1] - self.margin[1] - 16
		self.canvas.setFillColor(self.text_color)
		with TemporaryMarginIncrease(self, self.left_bar_width - self.margin[0] + 0.125 * 72):
			for section in sections:
				if section in self.resume.custom_sections:
					self.draw_custom_section(section)
				elif section == "WORK EXPERIENCE":
					self.draw_work_experience()

	def draw(self, sections: list):
		self._draw_left_bar()
		self._draw_right_bar(sections)
