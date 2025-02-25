from setuptools import setup, find_packages

setup(
    name="veda-base",
    version="0.1.0",
    description="A multi-agent system for knowledge management and document processing",
    author="@hams_ollo",
    packages=find_packages(),
    install_requires=[
        # Core Dependencies
        "streamlit>=1.24.0",
        "fastapi>=0.109.0",
        "uvicorn>=0.27.0",
        "pydantic>=2.5.3",
        "python-dotenv>=1.0.0",

        # Async and Networking
        "aiohttp>=3.8.5",
        "asyncio>=3.4.3",
        "websockets>=12.0",
        "python-multipart>=0.0.6",
        "aiofiles>=23.2.1",

        # Data Processing and Analysis
        "pandas>=2.0.3",
        "numpy>=1.24.3",
        "scikit-learn>=1.3.0",
        "scipy>=1.11.0",

        # Document Processing
        "python-docx>=0.8.11",
        "PyPDF2>=3.0.1",
        "PyMuPDF>=1.23.8",  # fitz
        "markdown>=3.4.3",
        "python-frontmatter>=1.0.0",
        "trafilatura>=2.0.0",
        "python-pptx>=0.6.22",
        "python-magic>=0.4.27",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
        "camelot-py>=0.11.0",

        # AI and Machine Learning
        "groq>=0.4.2",
        "langchain>=0.1.0",
        "langchain-groq>=0.0.1",
        "transformers>=4.38.1",
        "sentence-transformers>=2.2.2",
        "torch>=2.2.0",
        "accelerate>=0.27.0",
        "safetensors>=0.4.2",

        # Vector Storage and Databases
        "chromadb>=0.4.22",
        "sqlalchemy>=2.0.0",
        "alembic>=1.13.0",
        "psycopg2-binary>=2.9.9",

        # Visualization
        "plotly>=5.15.0",
        "networkx>=3.1",
        "pyvis>=0.3.2",
        "graphviz>=0.20.1",
        "matplotlib>=3.8.0",

        # Utilities
        "python-dateutil>=2.8.2",
        "pytz>=2023.3",
        "tqdm>=4.65.0",
        "pyyaml>=6.0.1",
        "python-slugify>=8.0.1",
        "cryptography>=41.0.0",
        "tenacity>=8.2.0",
        "diskcache>=5.6.1",
    ],
    extras_require={
        'dev': [
            # Testing
            "pytest>=7.4.0",
            "pytest-asyncio>=0.23.0",
            "pytest-cov>=4.1.0",
            "hypothesis>=6.92.0",

            # Development Tools
            "black>=23.12.0",
            "isort>=5.13.0",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
            "pre-commit>=3.6.0",

            # Documentation
            "sphinx>=7.1.0",
            "sphinx-rtd-theme>=1.3.0",
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.5.0",

            # Monitoring and Logging
            "prometheus-client>=0.19.0",
            "python-json-logger>=2.0.7",
            "opentelemetry-api>=1.21.0",
            "opentelemetry-sdk>=1.21.0",
        ],
    },
    python_requires=">=3.8",
) 