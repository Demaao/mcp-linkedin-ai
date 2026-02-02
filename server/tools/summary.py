from server.schemas import SummaryRequest, SummaryResponse

# Try to import the optional LLM-based summary improver.
# If unavailable, the system will fall back to rule-based logic.

try:
    from server.llm_client import improve_summary_with_llm
except ImportError:
    improve_summary_with_llm = None

# Role-specific keywords used to detect relevant experience in the summary
ROLE_KEYWORDS = {
    "backend developer": ["api", "backend", "server", "python", "java"],
    "frontend developer": ["react", "javascript", "frontend", "ui"],
    "data analyst": ["data", "sql", "analytics", "statistics"],
    "data scientist": ["data", "ml", "python", "statistics", "modeling"],
    "qa engineer": ["qa", "testing", "automation"],
    "devops engineer": ["ci/cd", "docker", "cloud", "automation"],
    "full stack developer": ["frontend", "backend", "react", "api"],
    "software engineer": ["software", "development", "code", "systems"],
    "mobile developer": ["mobile", "ios", "android", "react native", "swift", "kotlin"],
    "ml engineer": ["ml", "machine learning", "python", "model", "production"],
    "cloud engineer": ["cloud", "aws", "azure", "gcp", "infrastructure"],
    "security engineer": ["security", "application", "cloud", "compliance"],
    "product manager": ["product", "roadmap", "stakeholders", "agile"],
    "technical lead": ["architecture", "lead", "team", "technical"],
}

# Text markers that usually indicate a student or entry-level profile
NO_EXPERIENCE_MARKERS = [
    "student",
    "graduate",
    "looking for",
    "first opportunity",
    "motivated",
]

# Summary templates for experienced candidates, per role
ROLE_SUMMARY_TEMPLATES = {
    "backend developer": (
        "Backend Developer with hands-on experience building server-side logic, APIs, "
        "and data-driven systems, focusing on reliability and scalability."
    ),
    "frontend developer": (
        "Frontend Developer experienced in building user interfaces using modern "
        "JavaScript frameworks, with a strong focus on usability and performance."
    ),
    "data analyst": (
        "Data Analyst with experience working with data, statistics, and transforming "
        "raw data into actionable insights."
    ),
    "data scientist": (
        "Data Scientist with experience in machine learning, statistics, and turning "
        "data into models and business impact."
    ),
    "qa engineer": (
        "QA Engineer with experience in software testing, quality assurance processes, "
        "and ensuring system reliability."
    ),
    "devops engineer": (
        "DevOps Engineer with experience in CI/CD pipelines, cloud infrastructure, "
        "and automation."
    ),
    "full stack developer": (
        "Full Stack Developer experienced in both frontend and backend, building "
        "end-to-end applications with modern frameworks."
    ),
    "software engineer": (
        "Software Engineer with experience designing and building reliable systems "
        "and clean, maintainable code."
    ),
    "mobile developer": (
        "Mobile Developer experienced in building native or cross-platform apps "
        "for iOS and Android."
    ),
    "ml engineer": (
        "ML Engineer with experience taking machine learning models from research "
        "to production, including pipelines and monitoring."
    ),
    "cloud engineer": (
        "Cloud Engineer with experience in AWS, Azure, or GCP, infrastructure as code, "
        "and scalable architectures."
    ),
    "security engineer": (
        "Security Engineer focused on application and cloud security, compliance, "
        "and secure development practices."
    ),
    "product manager": (
        "Product Manager with experience defining roadmaps, working with stakeholders, "
        "and driving delivery in agile environments."
    ),
    "technical lead": (
        "Technical Lead with experience in architecture decisions, mentoring, "
        "and leading engineering teams."
    ),
}

STUDENT_SUMMARY_TEMPLATES = {
    "backend developer": (
        "Computer Science student with a strong foundation in backend development, "
        "experienced through academic and personal projects involving APIs, Python, "
        "and server-side systems."
    ),
    "frontend developer": (
        "Computer Science student with a focus on frontend development, experienced "
        "in building user interfaces using React and modern JavaScript through "
        "academic and personal projects."
    ),
    "data analyst": (
        "Student with a strong analytical background, experienced in data analysis, "
        "SQL, and statistics through academic coursework and projects."
    ),
    "data scientist": (
        "Student with a strong foundation in data science and ML, experienced in "
        "Python, statistics, and modeling through coursework and projects."
    ),
    "qa engineer": (
        "Computer Science student with a focus on software quality and testing, "
        "experienced in QA methodologies and testing tools through academic projects."
    ),
    "devops engineer": (
        "Computer Science student with hands-on experience in DevOps concepts such as "
        "CI/CD, automation, and cloud fundamentals through academic and personal projects."
    ),
    "full stack developer": (
        "Computer Science student with full stack experience through projects in "
        "frontend and backend technologies."
    ),
    "software engineer": (
        "Computer Science student building practical experience in software development "
        "through coursework and personal projects."
    ),
    "mobile developer": (
        "Student with experience in mobile development through projects in iOS, "
        "Android, or cross-platform frameworks."
    ),
    "ml engineer": (
        "Student with a focus on machine learning and ML systems, experienced through "
        "coursework and projects in Python and ML frameworks."
    ),
    "cloud engineer": (
        "Student with hands-on experience in cloud and infrastructure through "
        "courses and personal projects (AWS, Azure, or GCP)."
    ),
    "security engineer": (
        "Student with interest in security, experienced through coursework and "
        "projects in application or cloud security."
    ),
    "product manager": (
        "Student with interest in product management, experienced through projects "
        "in requirements, roadmap, and agile practices."
    ),
    "technical lead": (
        "Student with leadership experience in technical projects and team collaboration."
    ),
}


def rewrite_summary(data: SummaryRequest) -> SummaryResponse:
    # Try LLM first (if available and key is configured)
    if improve_summary_with_llm:
        llm_result = improve_summary_with_llm(
            data.current_summary,
            data.target_role,
        )
        if llm_result:
            return SummaryResponse(
                improved_summary=llm_result[0],
                explanation=llm_result[1],
                llm_used=True,
            )

    # Fallback: rule-based templates
    role_key = data.target_role.lower()
    summary_lower = (data.current_summary or "").lower()

    keywords = ROLE_KEYWORDS.get(role_key, [])
    has_experience = any(k in summary_lower for k in keywords)
    no_experience = any(marker in summary_lower for marker in NO_EXPERIENCE_MARKERS)

    if not has_experience or no_experience:
        summary = STUDENT_SUMMARY_TEMPLATES.get(
            role_key,
            f"Student with a strong interest in {data.target_role}, "
            f"building practical skills through academic studies and personal projects."
        )
        explanation = "Summary rewritten for a student or entry-level candidate."
    else:
        summary = ROLE_SUMMARY_TEMPLATES.get(
            role_key,
            f"{data.target_role} with a solid technical background and professional experience."
        )
        explanation = "Summary rewritten for an experienced candidate."

    return SummaryResponse(
        improved_summary=summary,
        explanation=explanation,
        llm_used=False,
    )