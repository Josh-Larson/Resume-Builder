from typing import List, Optional, Tuple
import re
import uuid

from data import Education, Resume, ResumeContentBlock

from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class ResumeGenerator:
	def __init__(self, resume: Resume, output_path: str):
		pdfmetrics.registerFont(TTFont("Calibri", "Calibri.ttf"))
		pdfmetrics.registerFont(TTFont("Calibri-Bold", "CalibriBold.ttf"))
		pdfmetrics.registerFont(TTFont("Symbola", "Symbola.ttf"))
		self.page_size = (8.5 * inch, 11 * inch)
		self.margin = (0.25 * inch, 0.25 * inch)
		self.default_font = ("Calibri", 12)
		self.pos = self.page_size[1] - self.margin[1]
		self.font = None
		self.resume = resume
		self.canvas = canvas.Canvas(output_path, pagesize=self.page_size)

	def _set_font(self, height: float, bold: bool):
		font_name = "Calibri-Bold" if bold else "Calibri"
		new_font = (font_name, height, bold)
		if self.font != new_font:
			self.canvas.setFont(font_name, height)
			self.font = new_font

	def _new_page(self):
		self.canvas.showPage()
		self.canvas.setFont(self.font[0], self.font[1])
		self.pos = self.page_size[1] - self.margin[1]

	def _split_line(self, line: str, font_height: float = None) -> Tuple[List[str], float]:
		font_height = font_height if font_height is not None else self.font[1]
		lines = []
		height = 0
		for line in line.split("\n"):
			if line == "":
				lines.append([])
				continue
			tokens = []
			start_index = 0
			# Find URLs
			text_uuid = uuid.uuid4()
			for match in re.finditer(r"\[([^]]+)]\(([^)]+)\)", line):
				if start_index < match.start():
					tokens.append({"type": "str", "text": line[start_index:match.start()], "uuid": text_uuid})
				tokens.append({"type": "url", "text": match.group(1), "url": match.group(2), "uuid": uuid.uuid4()})
				start_index = match.end()
			if start_index < len(line):
				tokens.append({"type": "str", "text": line[start_index:], "uuid": text_uuid})

			# Split tokens on words
			tokens_final = []
			for token in tokens:
				for word in token["text"].split(" "):
					token_copy = token.copy()
					token_copy["text"] = word
					tokens_final.append(token_copy)
			tokens = tokens_final

			line_tokens = []
			current_line_width = 0
			current_token: Optional[dict] = None
			for token in tokens:
				if current_token is not None and current_token["uuid"] != token["uuid"]:
					# Commit unique token to line
					line_tokens.append(current_token)
					current_token = None
				if current_token is None:
					current_token = token.copy()
					current_token["text"] = ""
				text = token["text"]
				prev_words_length = current_line_width + self.canvas.stringWidth(current_token["text"])
				next_word_length = self.canvas.stringWidth(text)
				if prev_words_length + next_word_length > self.page_size[0] - self.margin[0] * 2:
					line_tokens.append(current_token)
					lines.append(line_tokens)
					line_tokens = []
					current_token = None
					current_line_width = 0
					height += font_height + 2
				if current_token is not None:
					if len(current_token["text"]) > 0 or len(text) == 0:
						current_token["text"] += " "
					current_token["text"] += text
				if current_token is None:
					current_token = token.copy()
			if current_token is not None:
				line_tokens.append(current_token)
			if len(line_tokens) > 0:
				lines.append(line_tokens)
		return lines, height

	def _draw_table_row(self, row: List[str], width: List[float], height: List[float], bold: List[bool]):
		if max(height) > self.pos - self.margin[1]:
			self._new_page()
		max_height = 0
		for col, val in enumerate(row):
			self._set_font(height[col], bold[col])
			for line in self._split_line(val)[0]:
				self.canvas.drawString(self.margin[0] + sum(width[:col]), self.pos, line)
				max_height = max(max_height, height[col] + 2)
		self.pos -= max_height

	def _draw_token(self, token: dict, height: float, pos_x: float, bold: bool, underline: bool):
		self._set_font(height, bold)
		token_width = self.canvas.stringWidth(token["text"])
		self.canvas.drawString(pos_x, self.pos, token["text"])
		if underline or token["type"] in {"underline", "url"}:
			self.canvas.line(pos_x, self.pos - 2, pos_x + token_width, self.pos - 2)
		if token["type"] == "url":
			self.canvas.linkURL(token["url"], (pos_x, self.pos - 2, pos_x + token_width, self.pos + height))
		return token_width

	def _draw_left(self, line: str, height: float = 12, bold: bool = False, underline: bool = False):
		self._set_font(height, bold)
		for line in self._split_line(line)[0]:
			if self.pos < self.margin[1]:
				self._new_page()
				if line == "":
					continue
			print(line)
			idx = self.margin[0]
			for token in line:
				idx += self._draw_token(token, height, idx, bold, underline)
			self.pos -= height + 2

	def _draw_centered(self, line: str, height: float = 12, bold: bool = False):
		self._set_font(height, bold)
		for line in self._split_line(line)[0]:
			if height > self.pos - self.margin[1]:
				self._new_page()
				if line == "":
					continue
			print(line)
			line_width = sum(self.canvas.stringWidth(token["text"]) for token in line)
			idx = self.page_size[0] / 2 - line_width / 2
			for token in line:
				idx += self._draw_token(token, height, idx, bold, underline=False)
			self.pos -= height + 2

	def _draw_right(self, line: str, height: float = 12, bold: bool = False):
		self._set_font(height, bold)
		for line in self._split_line(line)[0]:
			if height > self.pos - self.margin[1]:
				self._new_page()
				if line == "":
					continue
			print(line)
			line_width = sum(self.canvas.stringWidth(token["text"]) for token in line)
			idx = self.page_size[0] - self.margin[0] - line_width
			for token in line:
				idx += self._draw_token(token, height, idx, bold, underline=False)
			self.pos -= height + 2

	def _get_resume_content_block_height(self, block: ResumeContentBlock) -> float:
		height = 16 + sum(14 if line is not None else 0 for line in [block.subtitle, block.start_day, block.location])
		height += sum(self._split_line(bullet, 12)[1] for bullet in block.description) if block.description else 0
		return height - 18 - 14  # The first header nor last line don't count towards our actual height

	def _draw_resume_content_block(self, block: ResumeContentBlock):
		if self._get_resume_content_block_height(block) > self.pos - self.margin[1]:
			self._new_page()
		self._draw_left(block.title, height=14, bold=True)
		if block.subtitle is not None:
			self._draw_left(block.subtitle)
		if block.start_day is not None:
			self._draw_left(f"{block.start_day.strftime('%b %Y')} - {block.end_day.strftime('%b %Y') if block.end_day else 'Present'}")
		if block.location is not None:
			self._draw_left(block.location)
		if block.description is not None:
			for bullet in block.description:
				if bullet.startswith("\t"):
					tabs = len(bullet) - len(bullet.lstrip("\t"))
					bullet = bullet.lstrip("\t")
					self._draw_left(f"{'    ' * tabs} \u2022 {bullet}")
				else:
					self._draw_left(f" \u2022 {bullet}")

	def draw_author(self):
		author = self.resume.author
		height = 18 + 14 * 4
		if height > self.pos - self.margin[1]:
			self._new_page()
		phone = re.sub("[^0-9]", "", author.phone)
		self._draw_centered(author.name.upper(), height=18, bold=True)
		self._draw_centered(f"({phone[:3]}) {phone[3:6]}-{phone[6:]}")
		self._draw_centered(author.email)
		self._draw_centered(author.address)
		self._draw_centered("")

	def draw_pitch(self):
		pitch = self.resume.pitch
		height = 14 * 4
		if height > self.pos - self.margin[1]:
			self._new_page()
		self._draw_left(pitch)
		self._draw_centered("")

	def draw_skills(self):
		skills = self.resume.skills
		if len(skills) == 0:
			return
		self._draw_centered("SKILLS", height=16, bold=True)
		self._draw_left("")
		skill_width = max(self.canvas.stringWidth(skill + ": ", self.default_font[0], 12) for skill in skills) + 8
		list_width = self.page_size[0] - self.margin[0] * 2 - skill_width
		for skill, skill_list in skills.items():
			self._draw_table_row([skill + ":", ", ".join(skill_list)], [skill_width, list_width], [12, 12], [True, False])
		self._draw_left("")

	def draw_work_experience(self):
		experience = self.resume.experience
		if len(experience) == 0:
			return
		height = 18 + self._get_resume_content_block_height(experience[0].content)
		if height > self.pos - self.margin[1]:
			self._new_page()
		self._draw_centered("WORK EXPERIENCE", height=16, bold=True)
		for exp in experience:
			self._draw_left("")
			self._draw_resume_content_block(exp.content)
		self._draw_left("")

	def draw_custom_section(self, section_name: str):
		section_contents = self.resume.custom_sections[section_name]
		section_height = 18 + (14 + 16 + sum(sum(self._split_line(bullet)[1] for bullet in section.description) for section in section_contents))
		if section_height > self.pos - self.margin[1]:
			self._new_page()
		self._draw_centered(section_name, height=16, bold=True)
		for section in section_contents:
			self._draw_left("")
			self._draw_resume_content_block(section)
		self._draw_left("")

	def draw_certifications(self):
		if len(self.resume.certifications) == 0:
			return
		height = 18 + 14 * 2 + 14 * len(self.resume.certifications)
		if height > self.pos - self.margin[1]:
			self._new_page()
		self._draw_centered("CERTIFICATIONS", height=16, bold=True)
		self._draw_left("")
		for cert in self.resume.certifications:
			self._draw_left(f"{cert.name}   [{cert.day.strftime('%b %Y')}]")
		self._draw_left("")

	def __draw_education_list(self, title: str, education_list: List[Education]):
		self._draw_centered(title, height=16, bold=True)
		for edu in education_list:
			self._draw_left("")
			self._draw_resume_content_block(edu.content)
		self._draw_left("")

	def draw_education(self):
		education = self.resume.education
		if len(education) == 0:
			return
		height = 14 * 4
		if height > self.pos - self.margin[1]:
			self._new_page()
		self.__draw_education_list("EDUCATION", education)

	def draw_courses(self):
		courses = self.resume.courses
		if len(courses) == 0:
			return
		height = 14 * 4
		if height > self.pos - self.margin[1]:
			self._new_page()
		self.__draw_education_list("COURSES", courses)

	def save(self):
		self.canvas.save()
