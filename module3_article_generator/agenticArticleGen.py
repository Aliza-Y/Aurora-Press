import os
import json
import argparse
import requests
from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from enum import Enum

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("article_generator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("agentic_article_generator")

# Enums and Data Classes
class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class AgentType(Enum):
    INPUT_VALIDATOR = "input_validator"
    ARTICLE_WRITER = "article_writer"
    HEADLINE_GENERATOR = "headline_generator"
    SUMMARY_GENERATOR = "summary_generator"
    CONTENT_VALIDATOR = "content_validator"
    OUTPUT_FORMATTER = "output_formatter"

@dataclass
class TaskResult:
    status: TaskStatus
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    agent_type: Optional[AgentType] = None
    timestamp: Optional[str] = None

@dataclass
class ArticleData:
    title: str
    keywords: List[str]
    summary: str
    style: str = "neutral"
    tone: str = "informative"
    length: int = 500
    summary_length: int = 125

@dataclass
class GeneratedContent:
    article_text: str
    headline: str
    summary: str
    metadata: Dict[str, Any]

# Constants
DEFAULT_ARTICLE_LENGTH = 500
DEFAULT_TONE = "informative"
DEFAULT_STYLE = "neutral"
DEFAULT_SUMMARY_LENGTH = 125

# Base Agent Class
class BaseAgent(ABC):
    """Abstract base class for all agents in the workflow."""
    
    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        self.logger = logging.getLogger(f"agent_{agent_type.value}")
    
    @abstractmethod
    def execute(self, input_data: Any) -> TaskResult:
        """Execute the agent's main task."""
        pass
    
    def log_start(self, task_description: str):
        """Log the start of a task."""
        self.logger.info(f"Starting {task_description}")
    
    def log_success(self, task_description: str, additional_info: str = ""):
        """Log successful completion of a task."""
        msg = f"Successfully completed {task_description}"
        if additional_info:
            msg += f" - {additional_info}"
        self.logger.info(msg)
    
    def log_error(self, task_description: str, error: str):
        """Log an error during task execution."""
        self.logger.error(f"Failed {task_description}: {error}")

# Configuration Manager
class ConfigManager:
    """Manages API configuration and environment variables."""
    
    @staticmethod
    def load_api_key() -> str:
        """Load Groq API key from environment variable or .env file."""
        try:
            from dotenv import load_dotenv
            load_dotenv()
            logger.info("Loaded .env file")
        except ImportError:
            logger.warning("python-dotenv not installed, can't load from .env file")
        
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        
        logger.info("Successfully loaded API key")
        return api_key
    
    @staticmethod
    def load_api_url() -> str:
        """Load Groq API URL from environment variable or use default."""
        return os.environ.get("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")
    
    @staticmethod
    def load_model_name() -> str:
        """Load model name from environment variable or use default."""
        return os.environ.get("GROQ_MODEL", "mixtral-8x7b-32768")

# LLM Service
class LLMService:
    """Service for making requests to the LLM API."""
    
    def __init__(self):
        self.api_key = ConfigManager.load_api_key()
        self.api_url = ConfigManager.load_api_url()
        self.model_name = ConfigManager.load_model_name()
    
    def make_request(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.7) -> str:
        """Make a request to the Groq API with the given prompt."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "You are a professional journalist with expertise in writing clear, accurate, and engaging news content."},
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": 0.9
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to Groq API: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status code: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during API request: {str(e)}")
            raise

# Individual Agents
class InputValidatorAgent(BaseAgent):
    """Agent responsible for validating and parsing input data."""
    
    def __init__(self):
        super().__init__(AgentType.INPUT_VALIDATOR)
    
    def execute(self, input_data: Dict[str, Any]) -> TaskResult:
        """Validate and parse input data."""
        self.log_start("input validation")
        
        try:
            required_fields = ["title", "keywords", "summary"]
            for field in required_fields:
                if field not in input_data:
                    raise ValueError(f"Required field '{field}' missing from input data")
            
            # Create ArticleData object with defaults
            article_data = ArticleData(
                title=input_data["title"],
                keywords=input_data["keywords"],
                summary=input_data["summary"],
                style=input_data.get("style", DEFAULT_STYLE),
                tone=input_data.get("tone", DEFAULT_TONE),
                length=input_data.get("length", DEFAULT_ARTICLE_LENGTH),
                summary_length=input_data.get("summary_length", DEFAULT_SUMMARY_LENGTH)
            )
            
            # Validate length parameters
            if not isinstance(article_data.length, int) or article_data.length <= 0:
                self.logger.warning(f"Invalid length: {article_data.length}. Using default: {DEFAULT_ARTICLE_LENGTH}")
                article_data.length = DEFAULT_ARTICLE_LENGTH
            
            if not isinstance(article_data.summary_length, int) or article_data.summary_length <= 0:
                self.logger.warning(f"Invalid summary length: {article_data.summary_length}. Using default: {DEFAULT_SUMMARY_LENGTH}")
                article_data.summary_length = DEFAULT_SUMMARY_LENGTH
            
            self.log_success("input validation", f"Title: {article_data.title}")
            
            return TaskResult(
                status=TaskStatus.COMPLETED,
                data=asdict(article_data),
                agent_type=self.agent_type,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            self.log_error("input validation", str(e))
            return TaskResult(
                status=TaskStatus.FAILED,
                error=str(e),
                agent_type=self.agent_type,
                timestamp=datetime.now().isoformat()
            )

class ArticleWriterAgent(BaseAgent):
    """Agent responsible for generating the main article content."""
    
    def __init__(self, llm_service: LLMService):
        super().__init__(AgentType.ARTICLE_WRITER)
        self.llm_service = llm_service
    
    def execute(self, article_data: ArticleData) -> TaskResult:
        """Generate the main article content."""
        self.log_start(f"article generation for: {article_data.title}")
        
        try:
            prompt = self._create_article_prompt(article_data)
            max_tokens = min(4000, article_data.length * 2)
            
            article_text = self.llm_service.make_request(prompt, max_tokens)
            word_count = len(article_text.split())
            
            self.log_success("article generation", f"Word count: {word_count}")
            
            return TaskResult(
                status=TaskStatus.COMPLETED,
                data={"article_text": article_text, "word_count": word_count},
                agent_type=self.agent_type,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            self.log_error("article generation", str(e))
            return TaskResult(
                status=TaskStatus.FAILED,
                error=str(e),
                agent_type=self.agent_type,
                timestamp=datetime.now().isoformat()
            )
    
    def _create_article_prompt(self, article_data: ArticleData) -> str:
        """Create a detailed prompt for the LLM to generate the main article."""
        keywords_str = ", ".join(article_data.keywords)
        return f"""
You are an expert news journalist writing a breaking news article about a trending topic. Focus on current events and newsworthy developments, not general background information.

TOPIC: {article_data.title}
CONTEXT/SUMMARY: {article_data.summary}
KEY ASPECTS TO COVER: {keywords_str}

ARTICLE REQUIREMENTS:
1. Focus on Recent Developments:
   - Cover the CURRENT news and developments about this topic
   - Focus on what's happening NOW, not general historical background
   - Include specific dates, figures, and relevant quotes if applicable
   - Address why this is newsworthy TODAY

2. Article Structure:
   - Strong news lead (first paragraph) highlighting the most important current development
   - Include relevant context ONLY if directly related to the current news
   - Target length: approximately {article_data.length} words
   - Use proper AP style for news writing
   - Write in an {article_data.style} style with a {article_data.tone} tone

3. Content Guidelines:
   - Stick to verifiable facts and current developments
   - Include relevant stakeholder perspectives
   - Focus on impact and implications of the current news
   - Avoid generic encyclopedia-style background unless directly relevant
   - Include specific details about the trending development
   - End with forward-looking implications or next steps

4. DO NOT:
   - Do not write a general overview or history unless directly relevant
   - Do not include unnecessary background information
   - Do not speculate beyond available facts
   - Do not editorialize unless writing an opinion piece

Write a NEWS ARTICLE about the CURRENT developments and trending aspects of this topic. Focus on what makes this newsworthy RIGHT NOW:
"""

class HeadlineGeneratorAgent(BaseAgent):
    """Agent responsible for generating article headlines."""
    
    def __init__(self, llm_service: LLMService):
        super().__init__(AgentType.HEADLINE_GENERATOR)
        self.llm_service = llm_service
    
    def execute(self, article_data: ArticleData) -> TaskResult:
        """Generate a headline for the article."""
        self.log_start(f"headline generation for: {article_data.title}")
        
        try:
            prompt = self._create_headline_prompt(article_data)
            headline = self.llm_service.make_request(prompt, max_tokens=100, temperature=0.7)
            
            # Clean up the headline
            clean_headline = self._clean_headline(headline)
            
            self.log_success("headline generation", f"Generated: {clean_headline}")
            
            return TaskResult(
                status=TaskStatus.COMPLETED,
                data={"headline": clean_headline},
                agent_type=self.agent_type,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            self.log_error("headline generation", str(e))
            return TaskResult(
                status=TaskStatus.FAILED,
                error=str(e),
                agent_type=self.agent_type,
                timestamp=datetime.now().isoformat()
            )
    
    def _create_headline_prompt(self, article_data: ArticleData) -> str:
        """Create a prompt for headline generation."""
        return f"""
Generate a single headline for this news story. Only output the headline text, nothing else.

CONTEXT:
Title: {article_data.title}
Summary: {article_data.summary}
Keywords: {", ".join(article_data.keywords)}

REQUIREMENTS:
- Create exactly ONE headline between 5-12 words
- Use active voice and strong action verbs
- Be attention-grabbing but factual
- Focus on the most newsworthy aspect
- DO NOT include any explanations or additional text
- DO NOT use quotes or special formatting

Output the headline text only.
"""
    
    def _clean_headline(self, headline: str) -> str:
        """Clean and format the generated headline."""
        # Remove any quotes, newlines, and extra spaces
        headline = headline.strip().replace('"', '').replace("'", '')
        
        # Split into lines and take the first non-empty line
        lines = [line.strip() for line in headline.split('\n') if line.strip()]
        if not lines:
            return ""
        
        # Take the first line and ensure proper capitalization
        headline = lines[0]
        
        # Capitalize first letter of major words (Title Case)
        # but keep articles and short prepositions lowercase
        lowercase_words = {'a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'in', 'to', 'on', 'at', 'by', 'of'}
        # Common acronyms that should be all caps
        acronyms = {'ai', 'ml', 'nlp', 'api', 'ui', 'ux', 'ar', 'vr', 'iot'}
        
        words = headline.split()
        if not words:
            return ""
        
        # Always capitalize the first word unless it's an acronym
        if words[0].lower() in acronyms:
            words[0] = words[0].upper()
        else:
            words[0] = words[0].capitalize()
        
        # Capitalize other words unless they're in lowercase_words
        for i in range(1, len(words)):
            word_lower = words[i].lower()
            if word_lower in acronyms:
                words[i] = word_lower.upper()
            elif word_lower not in lowercase_words:
                words[i] = words[i].capitalize()
            else:
                words[i] = word_lower
        
        return ' '.join(words)

class SummaryGeneratorAgent(BaseAgent):
    """Agent responsible for generating article summaries."""
    
    def __init__(self, llm_service: LLMService):
        super().__init__(AgentType.SUMMARY_GENERATOR)
        self.llm_service = llm_service
    
    def execute(self, article_data: ArticleData) -> TaskResult:
        """Generate an article summary."""
        self.log_start(f"summary generation for: {article_data.title}")
        
        try:
            prompt = self._create_summary_prompt(article_data)
            summary_text = self.llm_service.make_request(prompt, max_tokens=400, temperature=0.6)
            word_count = len(summary_text.split())
            
            self.log_success("summary generation", f"Word count: {word_count}")
            
            return TaskResult(
                status=TaskStatus.COMPLETED,
                data={"summary": summary_text, "word_count": word_count},
                agent_type=self.agent_type,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            self.log_error("summary generation", str(e))
            return TaskResult(
                status=TaskStatus.FAILED,
                error=str(e),
                agent_type=self.agent_type,
                timestamp=datetime.now().isoformat()
            )
    
    def _create_summary_prompt(self, article_data: ArticleData) -> str:
        """Create a prompt for generating an article summary."""
        keywords_str = ", ".join(article_data.keywords)
        return f"""
You are a professional news editor creating a concise summary for a news article. Based on the following information, write a compelling summary:

ARTICLE TITLE: {article_data.title}
ARTICLE CONTEXT: {article_data.summary}
KEYWORDS: {keywords_str}
STYLE: {article_data.style}
TONE: {article_data.tone}

ARTICLE TEXT TO SUMMARIZE:
{article_data.article_text}

REQUIREMENTS:
- Write a summary of exactly {article_data.summary_length} words
- Focus on the most important facts and key points from the article
- Include the main developments and their significance
- Use professional journalistic writing style
- Be engaging and informative
- Write in third person
- Use clear, concise language
- Make it suitable for use as a meta description or article preview
- Ensure it captures the essence of the full article
- Do not include phrases like "this article discusses" or similar meta-references

Create a professional news article summary of {article_data.summary_length} words that captures the key points:
"""

class ContentValidatorAgent(BaseAgent):
    """Agent responsible for validating generated content quality."""
    
    def __init__(self):
        super().__init__(AgentType.CONTENT_VALIDATOR)
    
    def execute(self, content: GeneratedContent, article_data: ArticleData) -> TaskResult:
        """Validate all generated content and provide comprehensive metadata."""
        self.log_start("content validation")
        
        try:
            metadata = self._validate_content(content, article_data)
            self.log_success("content validation", "All content validated")
            
            return TaskResult(
                status=TaskStatus.COMPLETED,
                data={"metadata": metadata},
                agent_type=self.agent_type,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            self.log_error("content validation", str(e))
            return TaskResult(
                status=TaskStatus.FAILED,
                error=str(e),
                agent_type=self.agent_type,
                timestamp=datetime.now().isoformat()
            )
    
    def _validate_content(self, content: GeneratedContent, article_data: ArticleData) -> Dict[str, Any]:
        """Validate all generated content and provide comprehensive metadata."""
        article_word_count = len(content.article_text.split())
        summary_word_count = len(content.summary.split())
        headline_word_count = len(content.headline.split())
        
        target_length = article_data.length
        target_summary_length = article_data.summary_length
        
        # Calculate differences
        article_length_difference = abs(article_word_count - target_length)
        article_length_percentage = (article_length_difference / target_length) * 100
        
        summary_length_difference = abs(summary_word_count - target_summary_length)
        summary_length_percentage = (summary_length_difference / target_summary_length) * 100
        
        # Check keyword coverage
        keywords_in_article = [keyword.lower() in content.article_text.lower() for keyword in article_data.keywords]
        keywords_in_summary = [keyword.lower() in content.summary.lower() for keyword in article_data.keywords]
        keywords_in_headline = [keyword.lower() in content.headline.lower() for keyword in article_data.keywords]
        
        missing_keywords_article = [
            article_data.keywords[i] for i in range(len(article_data.keywords))
            if not keywords_in_article[i]
        ]
        missing_keywords_summary = [
            article_data.keywords[i] for i in range(len(article_data.keywords))
            if not keywords_in_summary[i]
        ]
        
        metadata = {
            "article": {
                "word_count": article_word_count,
                "target_length": target_length,
                "length_difference": article_length_difference,
                "length_difference_percentage": article_length_percentage
            },
            "headline": {
                "word_count": headline_word_count,
                "text": content.headline,
                "keywords_present": sum(keywords_in_headline)
            },
            "summary": {
                "word_count": summary_word_count,
                "target_length": target_summary_length,
                "length_difference": summary_length_difference,
                "length_difference_percentage": summary_length_percentage
            },
            "keywords_coverage": {
                "total": len(article_data.keywords),
                "article_coverage": {
                    "present": sum(keywords_in_article),
                    "missing": missing_keywords_article
                },
                "summary_coverage": {
                    "present": sum(keywords_in_summary),
                    "missing": missing_keywords_summary
                },
                "headline_coverage": {
                    "present": sum(keywords_in_headline)
                }
            },
            "title": article_data.title,
            "generated_timestamp": datetime.now().isoformat()
        }
        
        # Log quality warnings
        self._log_quality_warnings(metadata, missing_keywords_article, missing_keywords_summary)
        
        return metadata
    
    def _log_quality_warnings(self, metadata: Dict[str, Any], missing_keywords_article: List[str], missing_keywords_summary: List[str]):
        """Log warnings for quality issues."""
        if metadata["article"]["length_difference_percentage"] > 20:
            self.logger.warning(f"Article length ({metadata['article']['word_count']} words) differs significantly from target ({metadata['article']['target_length']} words)")
        
        if metadata["summary"]["length_difference_percentage"] > 25:
            self.logger.warning(f"Summary length ({metadata['summary']['word_count']} words) differs from target ({metadata['summary']['target_length']} words)")
        
        if metadata["headline"]["word_count"] > 15:
            self.logger.warning(f"Headline is quite long ({metadata['headline']['word_count']} words). Consider shortening.")
        
        if missing_keywords_article:
            self.logger.warning(f"Some keywords missing from article: {', '.join(missing_keywords_article)}")
        
        if missing_keywords_summary:
            self.logger.warning(f"Some keywords missing from summary: {', '.join(missing_keywords_summary)}")

class OutputFormatterAgent(BaseAgent):
    """Agent responsible for formatting the final output."""
    
    def __init__(self):
        super().__init__(AgentType.OUTPUT_FORMATTER)
    
    def execute(self, content: GeneratedContent) -> TaskResult:
        """Format the final output to be passed to other agents."""
        self.log_start("output formatting")
        
        try:
            output = {
                "headline": content.headline,
                "article_text": content.article_text,
                "summary": content.summary,
                "title": content.metadata.get("title", ""),
                "metadata": content.metadata,
                "status": "success",
                "agent": "article_generation"
            }
            
            self.log_success("output formatting", "Output formatted successfully")
            
            return TaskResult(
                status=TaskStatus.COMPLETED,
                data=output,
                agent_type=self.agent_type,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            self.log_error("output formatting", str(e))
            return TaskResult(
                status=TaskStatus.FAILED,
                error=str(e),
                agent_type=self.agent_type,
                timestamp=datetime.now().isoformat()
            )

# Workflow Orchestrator
class ArticleGenerationWorkflow:
    """Main workflow orchestrator that coordinates all agents."""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.agents = {
            AgentType.INPUT_VALIDATOR: InputValidatorAgent(),
            AgentType.ARTICLE_WRITER: ArticleWriterAgent(self.llm_service),
            AgentType.HEADLINE_GENERATOR: HeadlineGeneratorAgent(self.llm_service),
            AgentType.SUMMARY_GENERATOR: SummaryGeneratorAgent(self.llm_service),
            AgentType.CONTENT_VALIDATOR: ContentValidatorAgent(),
            AgentType.OUTPUT_FORMATTER: OutputFormatterAgent()
        }
        self.logger = logging.getLogger("workflow_orchestrator")
    
    def execute_workflow(self, input_json: str) -> str:
        """Execute the complete article generation workflow."""
        try:
            # Parse input JSON
            input_data = json.loads(input_json)
            self.logger.info("Starting agentic article generation workflow")
            
            # Step 1: Validate input
            validation_result = self.agents[AgentType.INPUT_VALIDATOR].execute(input_data)
            if validation_result.status == TaskStatus.FAILED:
                return self._format_error_response(validation_result.error, "input_validation")
            
            article_data = ArticleData(**validation_result.data)
            
            # Step 2: Generate article content
            article_result = self.agents[AgentType.ARTICLE_WRITER].execute(article_data)
            if article_result.status == TaskStatus.FAILED:
                return self._format_error_response(article_result.error, "article_generation")
            
            headline_result = self.agents[AgentType.HEADLINE_GENERATOR].execute(article_data)
            if headline_result.status == TaskStatus.FAILED:
                return self._format_error_response(headline_result.error, "headline_generation")
            
            # Update article_data with the generated article text for summary generation
            article_data.article_text = article_result.data["article_text"]
            
            summary_result = self.agents[AgentType.SUMMARY_GENERATOR].execute(article_data)
            if summary_result.status == TaskStatus.FAILED:
                return self._format_error_response(summary_result.error, "summary_generation")
            
            # Step 3: Create generated content object
            generated_content = GeneratedContent(
                article_text=article_result.data["article_text"],
                headline=headline_result.data["headline"],
                summary=summary_result.data["summary"],
                metadata={}
            )
            
            # Step 4: Validate content
            validation_result = self.agents[AgentType.CONTENT_VALIDATOR].execute(generated_content, article_data)
            if validation_result.status == TaskStatus.FAILED:
                return self._format_error_response(validation_result.error, "content_validation")
            
            # Update content with metadata
            generated_content.metadata = validation_result.data["metadata"]
            
            # Step 5: Format output
            output_result = self.agents[AgentType.OUTPUT_FORMATTER].execute(generated_content)
            if output_result.status == TaskStatus.FAILED:
                return self._format_error_response(output_result.error, "output_formatting")
            
            self.logger.info("Agentic workflow completed successfully")
            return json.dumps(output_result.data, indent=2)
            
        except json.JSONDecodeError as e:
            return self._format_error_response(f"Invalid JSON input: {str(e)}", "json_parsing")
        except Exception as e:
            return self._format_error_response(f"Unexpected workflow error: {str(e)}", "workflow_execution")
    
    def _format_error_response(self, error_message: str, error_type: str) -> str:
        """Format error response in consistent JSON format."""
        return json.dumps({
            "status": "error",
            "message": error_message,
            "error_type": error_type,
            "agent": "agentic_article_generation",
            "timestamp": datetime.now().isoformat()
        })

def process_article_request(input_json: str) -> str:
    """
    Process an article generation request from the trend API.
    This function bridges the old and new article generation systems.
    
    Args:
        input_json (str): JSON string containing article generation parameters
        
    Returns:
        str: JSON string containing the generated article and metadata
    """
    try:
        # Initialize the workflow
        workflow = ArticleGenerationWorkflow()
        
        # Execute the workflow and return results
        return workflow.execute_workflow(input_json)
        
    except Exception as e:
        error_response = {
            "status": "error",
            "message": str(e),
            "error_type": "article_generation",
            "agent": "agentic_article_generation",
            "timestamp": datetime.now().isoformat()
        }
        return json.dumps(error_response)

# CLI Interface
def main():
    """Command-line entry point for the Agentic Article Generation Workflow."""
    parser = argparse.ArgumentParser(description="Agentic Article Generation Workflow")
    parser.add_argument(
        "-i", "--input",
        help="Input JSON file from News Crawler Agent",
        type=str
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file for the generated content",
        type=str
    )
    
    args = parser.parse_args()
    
    # Initialize workflow
    workflow = ArticleGenerationWorkflow()
    
    # Process from file if provided, otherwise from stdin
    if args.input:
        try:
            with open(args.input, 'r') as f:
                input_json = f.read()
        except FileNotFoundError:
            logger.error(f"Input file not found: {args.input}")
            return 1
    else:
        logger.info("Reading input from stdin...")
        input_json = input("Enter JSON input from News Crawler Agent: ")
    
    # Execute workflow
    output_json = workflow.execute_workflow(input_json)
    
    # Write to file if specified, otherwise print to stdout
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(output_json)
            logger.info(f"Output written to: {args.output}")
        except Exception as e:
            logger.error(f"Error writing to output file: {str(e)}")
            return 1
    else:
        print(output_json)
    
    return 0

if __name__ == "__main__":
    exit(main())