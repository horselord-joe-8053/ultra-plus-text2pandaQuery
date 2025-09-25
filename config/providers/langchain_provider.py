#!/usr/bin/env python3
"""
LangChain-specific provider configurations and wrappers.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List
from .registry import ProviderConfig, LLMWrapper

# LangChain imports (lazy loading to avoid dependency issues)
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

try:
    from langchain_anthropic import ChatAnthropic
except ImportError:
    ChatAnthropic = None

try:
    from langchain_experimental.tools import PythonREPL
except ImportError:
    PythonREPL = None

try:
    from langchain.agents import initialize_agent, AgentType
except ImportError:
    initialize_agent = None
    AgentType = None


@dataclass
class LangChainProviderConfig(ProviderConfig):
    """Extended provider configuration for LangChain-specific features."""
    
    # LangChain specific settings
    langchain_provider: str = "openai"  # openai, google, anthropic
    use_agent: bool = True
    agent_type: str = "ZERO_SHOT_REACT_DESCRIPTION"
    python_repl_enabled: bool = True
    verbose: bool = False
    
    # Agent configuration
    max_iterations: int = 5
    early_stopping_method: str = "generate"
    
    # LangChain-specific extras
    langchain_extras: Dict[str, Any] = field(default_factory=dict)


class LangChainLLMWrapper(LLMWrapper):
    """Wrapper for LangChain LLM instances with agent support."""
    
    def __init__(self, config: LangChainProviderConfig):
        super().__init__(config)
        self.langchain_config = config
        self.llm = None
        self.agent = None
        self.python_repl = None
        
        # Initialize LangChain components
        self._initialize_langchain()
    
    def _initialize_langchain(self):
        """Initialize LangChain LLM and agent components."""
        provider = self.langchain_config.langchain_provider.lower()
        
        # Create LangChain LLM instance
        if provider == "openai":
            if ChatOpenAI is None:
                raise ImportError("langchain_openai is not available. Install with: pip install langchain-openai")
            
            self.llm = ChatOpenAI(
                model=self.model,
                api_key=self.config.credentials.get("api_key", ""),
                temperature=self.config.extras.get("temperature", 0.2),
                max_tokens=self.config.extras.get("max_tokens", 2048),
            )
            
        elif provider == "google":
            if ChatGoogleGenerativeAI is None:
                raise ImportError("langchain_google_genai is not available. Install with: pip install langchain-google-genai")
            
            self.llm = ChatGoogleGenerativeAI(
                model=self.model,
                google_api_key=self.config.credentials.get("api_key", ""),
                temperature=self.config.extras.get("temperature", 0.2),
                max_output_tokens=self.config.extras.get("max_tokens", 2048),
            )
            
        elif provider == "anthropic":
            if ChatAnthropic is None:
                raise ImportError("langchain_anthropic is not available. Install with: pip install langchain-anthropic")
            
            self.llm = ChatAnthropic(
                model=self.model,
                anthropic_api_key=self.config.credentials.get("api_key", ""),
                temperature=self.config.extras.get("temperature", 0.2),
                max_tokens=self.config.extras.get("max_tokens", 2048),
            )
            
        else:
            raise ValueError(f"Unsupported LangChain provider: {provider}")
        
        # Initialize PythonREPL if enabled
        if self.langchain_config.python_repl_enabled:
            if PythonREPL is None:
                raise ImportError("langchain_experimental is not available. Install with: pip install langchain-experimental")
            self.python_repl = PythonREPL()
        
        # Initialize agent if enabled
        if self.langchain_config.use_agent and self.python_repl:
            if initialize_agent is None or AgentType is None:
                raise ImportError("langchain agents are not available. Install with: pip install langchain")
            
            agent_type = getattr(AgentType, self.langchain_config.agent_type, AgentType.ZERO_SHOT_REACT_DESCRIPTION)
            
            self.agent = initialize_agent(
                tools=[self.python_repl],
                llm=self.llm,
                agent=agent_type,
                verbose=self.langchain_config.verbose,
                max_iterations=self.langchain_config.max_iterations,
                early_stopping_method=self.langchain_config.early_stopping_method,
            )
    
    def generate_content(self, contents: List[str]) -> str:
        """Generate content using LangChain LLM."""
        try:
            if not self.llm:
                raise RuntimeError("LangChain LLM not initialized")
            
            # Combine contents into a single prompt
            prompt = "\n".join(contents)
            
            # Use LangChain's invoke method
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
            
        except Exception as e:
            raise RuntimeError(f"LangChain generation failed: {e}")
    
    def generate_with_agent(self, query: str, context: Dict[str, Any] = None) -> str:
        """Generate content using LangChain agent with PythonREPL."""
        try:
            if not self.agent:
                raise RuntimeError("LangChain agent not initialized")
            
            # Build context for the agent
            context_str = ""
            if context:
                context_str = f"\nContext: {context}"
            
            full_query = f"{query}{context_str}"
            
            # Use agent to run the query
            result = self.agent.run(full_query)
            return str(result)
            
        except Exception as e:
            raise RuntimeError(f"LangChain agent execution failed: {e}")
    
    def is_agent_available(self) -> bool:
        """Check if agent is available and configured."""
        return self.agent is not None
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools for the agent."""
        if self.agent:
            return [tool.name for tool in self.agent.tools]
        return []


class LangChainFactory:
    """Factory for creating LangChain-based providers."""
    
    @staticmethod
    def create(config: LangChainProviderConfig) -> LangChainLLMWrapper:
        """Create a LangChain provider instance."""
        return LangChainLLMWrapper(config)
    
    @staticmethod
    def create_from_base_config(base_config: ProviderConfig, langchain_provider: str = "openai") -> LangChainProviderConfig:
        """Create LangChain config from base provider config."""
        return LangChainProviderConfig(
            provider=base_config.provider,
            generation_model=base_config.generation_model,
            embedding_model=base_config.embedding_model,
            credentials=base_config.credentials,
            extras=base_config.extras,
            langchain_provider=langchain_provider,
            use_agent=True,
            python_repl_enabled=True,
            verbose=False
        )
