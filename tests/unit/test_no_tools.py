#!/usr/bin/env python3
"""
Test suite for tools=None (--no-tools) functionality
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from groqqy import Groqqy, Agent
from groqqy.tool import ToolRegistry
from groqqy.providers.groq import GroqProvider


def test_groqqy_with_none_tools():
    """Groqqy should accept tools=None without creating default registry"""
    with patch.object(GroqProvider, '__init__', return_value=None):
        bot = Groqqy(tools=None)
        assert bot.tools is None


def test_groqqy_with_none_tools_no_defaults():
    """Groqqy with tools=None should NOT create default tools"""
    with patch.object(GroqProvider, '__init__', return_value=None):
        bot = Groqqy(tools=None)
        # Should be None, not an empty registry or default registry
        assert bot.tools is None
        assert not isinstance(bot.tools, ToolRegistry)


def test_groqqy_with_empty_registry_creates_defaults():
    """Groqqy with no tools parameter should create default registry"""
    with patch.object(GroqProvider, '__init__', return_value=None):
        bot = Groqqy()  # No tools parameter
        # Should create default registry
        assert bot.tools is not None
        assert isinstance(bot.tools, ToolRegistry)


def test_groqqy_tools_none_vs_empty():
    """Verify explicit None is different from empty/default"""
    with patch.object(GroqProvider, '__init__', return_value=None):
        # Explicit None = no tools at all
        bot_none = Groqqy(tools=None)
        assert bot_none.tools is None

        # No parameter = defaults
        bot_default = Groqqy()
        assert bot_default.tools is not None

        # Empty registry = explicit empty (still a registry object)
        bot_empty = Groqqy(tools=ToolRegistry())
        assert bot_empty.tools is not None
        assert isinstance(bot_empty.tools, ToolRegistry)


def test_agent_with_none_tools():
    """Agent should handle tools=None gracefully"""
    from groqqy.components import ConversationManager, ToolExecutor, CostTracker
    from groqqy.log import AgentLogger

    with patch.object(GroqProvider, '__init__', return_value=None):
        provider = Mock(spec=GroqProvider)
        conversation = Mock(spec=ConversationManager)
        executor = Mock(spec=ToolExecutor)
        tracker = Mock(spec=CostTracker)
        log = Mock(spec=AgentLogger)

        # Agent should accept tools=None
        agent = Agent(
            provider=provider,
            conversation=conversation,
            executor=executor,
            tracker=tracker,
            log=log,
            tools=None
        )

        assert agent.tools is None


def test_agent_strategy_with_none_tools():
    """Agent with tools=None should use LocalToolStrategy fallback"""
    from groqqy.components import ConversationManager, ToolExecutor, CostTracker
    from groqqy.log import AgentLogger
    from groqqy.strategy import LocalToolStrategy

    with patch.object(GroqProvider, '__init__', return_value=None):
        provider = Mock(spec=GroqProvider)
        conversation = Mock(spec=ConversationManager)
        executor = Mock(spec=ToolExecutor)
        tracker = Mock(spec=CostTracker)
        log = Mock(spec=AgentLogger)

        # Agent with None tools should create LocalToolStrategy fallback
        agent = Agent(
            provider=provider,
            conversation=conversation,
            executor=executor,
            tracker=tracker,
            log=log,
            tools=None
        )

        assert isinstance(agent.strategy, LocalToolStrategy)


def test_agent_call_llm_with_none_tools():
    """Agent._call_llm should pass None to provider when tools=None"""
    from groqqy.components import ConversationManager, ToolExecutor, CostTracker
    from groqqy.log import AgentLogger

    with patch.object(GroqProvider, '__init__', return_value=None):
        provider = Mock(spec=GroqProvider)
        conversation = Mock(spec=ConversationManager)
        conversation.get_history.return_value = []
        executor = Mock(spec=ToolExecutor)
        tracker = Mock(spec=CostTracker)
        log = Mock(spec=AgentLogger)

        # Mock provider.chat to return a response
        mock_response = Mock()
        mock_response.text = "test response"
        provider.chat.return_value = mock_response

        agent = Agent(
            provider=provider,
            conversation=conversation,
            executor=executor,
            tracker=tracker,
            log=log,
            tools=None
        )

        # Call _call_llm
        agent._call_llm()

        # Verify provider.chat was called with tools=None
        provider.chat.assert_called_once()
        call_kwargs = provider.chat.call_args[1]
        assert call_kwargs['tools'] is None


def test_agent_handle_response_with_none_tools():
    """Agent strategy.handle_response should work with None tools"""
    from groqqy.components import ConversationManager, ToolExecutor, CostTracker
    from groqqy.log import AgentLogger

    with patch.object(GroqProvider, '__init__', return_value=None):
        provider = Mock(spec=GroqProvider)
        conversation = Mock(spec=ConversationManager)
        executor = Mock(spec=ToolExecutor)
        tracker = Mock(spec=CostTracker)
        log = Mock(spec=AgentLogger)

        agent = Agent(
            provider=provider,
            conversation=conversation,
            executor=executor,
            tracker=tracker,
            log=log,
            tools=None
        )

        # Mock response
        mock_response = Mock()
        mock_response.text = "test response"

        # Should handle response without tools (empty list passed to strategy)
        # This shouldn't raise an exception
        result = agent.strategy.handle_response(mock_response, [])
        assert result is not None
