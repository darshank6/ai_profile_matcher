import re

import spacy

nlp = spacy.load(
    "en_core_web_md"
)

SKILLS = [

    "python",
    "fastapi",
    "django",
    "flask",

    "sql",
    "postgresql",
    "mysql",

    "sqlalchemy",
    "alembic",

    "docker",
    "kubernetes",

    "redis",
    "celery",

    "git",
    "github",

    "aws",
    "azure",

    "javascript",
    "typescript",

    "react",
    "angular",

    "langchain",
    "openai",

    "rag",

    "machine learning",

    "deep learning",

    "tensorflow",

    "pytorch",

    "pandas",

    "numpy"
]


def extract_skills(
    text: str
):

    text = text.lower()

    nlp(text)

    found_skills = set()

    for skill in SKILLS:

        if skill in text:

            found_skills.add(skill)

    patterns = [

        r"python",
        r"fastapi",
        r"django",
        r"docker",
        r"redis",
        r"postgresql",
        r"sqlalchemy",
        r"langchain",
        r"openai",
        r"rag"

    ]

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text
        )

        if matches:

            found_skills.add(
                pattern
            )

    return sorted(
        list(found_skills)
    )