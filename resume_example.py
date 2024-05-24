from datetime import date

from data import Resume, ResumeContentBlock, Author, WorkExperience, Certification, Education
from resume_generator import ResumeGenerator

resume = Resume(
	author=Author(
		name="John Doe",
		phone="(123) 456-7890",
		email="johnnydoe@gmail.com",
		address="1234 Elm Street, Apt 56, Some City, ST 12345"
	),
	pitch="Innovative and detail-oriented software engineer with 5+ years of experience in designing, developing, "
	      "and maintaining software applications. Proven expertise in full-stack development, agile methodologies, "
	      "and team collaboration. Committed to delivering high-quality, scalable solutions that meet business objectives "
	      "and enhance user experience.",
	skills={
		"Languages": ["Java", "Python", "JavaScript", "TypeScript", "SQL", "C++"],
		"Frameworks/Libraries": ["React", "Angular", "Node.js", "Spring Boot", "Django"],
		"Tools": ["Git", "Docker", "Kubernetes", "Jenkins", "JIRA", "AWS"],
		"Databases": ["MySQL", "PostgreSQL", "MongoDB", "Redis"],
		"Methodologies": ["Agile", "Scrum", "TDD (Test-Driven Development)"],
	},
	experience=[
		WorkExperience(
			company="ABC Tech Solutions",
			job_title="Software Engineer",
			location="Some City, TX",
			start_day=date(2020, 1, 1),
			end_day=None,
			description=[
				"Designed and developed scalable web applications using React, Node.js, and MongoDB, enhancing user experience and application performance.",
				"Led the migration of legacy systems to modern cloud-based architectures on AWS, reducing operational costs by 20%.",
				"Implemented CI/CD pipelines using Jenkins and Docker, significantly speeding up the deployment process and reducing errors.",
				"Collaborated with cross-functional teams to gather requirements, develop solutions, and ensure timely delivery of projects.",
				"Mentored junior developers, conducting code reviews and providing guidance on best practices.",
			]
		),
		WorkExperience(
			company="XYZ Innovations",
			job_title="Full Stack Developer",
			location="Another City, TX",
			start_day=date(2016, 6, 1),
			end_day=date(2019, 12, 1),
			description=[
				"Developed and maintained web applications using Angular, Spring Boot, and PostgreSQL, contributing to a 30% increase in user engagement.",
				"Created RESTful APIs to support front-end functionality.",
				"Improved application performance by optimizing SQL queries and implementing caching mechanisms.",
				"Participated in daily stand-ups, sprint planning, and retrospectives as part of the agile development process.",
				"Conducted unit and integration testing to ensure high-quality code and reduce the number of bugs in production.",
			]
		),
	],
	custom_sections={
		"PROJECTS": [
			ResumeContentBlock(
				title="Project Management Tool",
				description=[
					"Developed a web-based project management tool using React, Node.js, and MongoDB, enabling "
					"teams to track progress, manage tasks, and collaborate effectively.",
					"Implemented role-based access control and real-time notifications using WebSockets.",
				]
			),
			ResumeContentBlock(
				title="E-commerce Platform",
				description=[
					"Designed and built an e-commerce platform using Angular and Spring Boot, featuring a responsive UI, "
					"secure payment gateway integration, and order management system.",
					"Optimized the platform for high traffic and improved load times by implementing lazy loading and code splitting.",
				]
			),
		],
		"VOLUNTEER EXPERIENCE": [
			ResumeContentBlock(
				title="Code Mentor",
				subtitle="Non-Profit Coding Organization",
				start_day=date(2018, 6, 1),
				description=[
					"Provided mentorship to aspiring software developers, conducting workshops on web development, data structures, and algorithms.",
					"Assisted mentees with coding challenges, career advice, and resume building."
				]
			)
		],
	},
	certifications=[
		Certification("AWS Certified Solutions Architect – Associate", date(2023, 9, 1)),
		Certification("Certified ScrumMaster (CSM)", date(2021, 4, 1)),
		Certification("Oracle Certified Professional, Java SE 8 Programmer", date(2020, 8, 1)),
	],
	education=[
		Education(
			school="Northern University of Technology",
			course="Master of Science in Computer Science",
			location="Techville, TX",
			gpa=3.90,
			start_day=date(201, 8, 1),
			end_day=date(2018, 5, 1),
			description=[]
		),
		Education(
			school="Western Institute of Technology",
			course="Bachelor of Science in Computer Science",
			location="Innovate City, CA",
			gpa=3.70,
			start_day=date(2012, 8, 1),
			end_day=date(2016, 5, 1),
			description=[]
		),
	],
	courses=[],
)

gen = ResumeGenerator(resume, "resume_example.pdf")
gen.draw_author()
gen.draw_pitch()
gen.draw_skills()
gen.draw_work_experience()
gen.draw_certifications()
gen.draw_custom_section("PROJECTS")
gen.draw_education()
gen.draw_courses()
gen.draw_custom_section("VOLUNTEER EXPERIENCE")
gen.save()
