# Groqqy Teaching Guide

**How to use Groqqy to learn and teach agentic AI**

---

## 🎯 Who This Guide Is For

- **Students**: Learning agentic AI fundamentals
- **Educators**: Teaching AI agents in courses/workshops
- **Self-learners**: Exploring agentic patterns hands-on
- **Developers**: Understanding agent architecture before building

---

## Why Groqqy for Teaching?

### Problem: Most Agentic Frameworks Are Too Complex

**LangChain, LangGraph, AutoGPT** are production-grade but pedagogically challenging:
- 50,000+ lines of code
- 8+ abstraction layers
- Days to understand core patterns
- Hard to modify internals

### Groqqy's Solution: Pedagogical Simplicity

- ✅ **175 lines** for complete agentic loop
- ✅ **All files <200 lines** - fits on one screen
- ✅ **88-line core algorithm** - read in 5 minutes
- ✅ **Explicit comments** - THINK/ACT/OBSERVE labeled
- ✅ **Production patterns** - not toy code
- ✅ **1-2 hours to understand** - then extend it

**Teaching sweet spot:** Simple enough to grasp quickly, sophisticated enough to be real.

---

## 🎓 Learning Path

### Phase 1: Understanding (30-60 minutes)

**Goal:** Understand what agentic AI is and how it works

#### Step 1: Read the README (10 min)
- Start: [README.md](README.md)
- Focus on "Agentic Loop" diagram
- Understand THINK → ACT → OBSERVE pattern

#### Step 2: Read the Core Algorithm (15 min)
- File: `groqqy/agent.py:70-157`
- This is THE code that implements agentic behavior
- Comments explain each step

```python
# The agentic loop - read this carefully!
while iteration < self.max_iterations:
    # THINK: What should I do next?
    response = self._call_llm()

    # ACT: Execute tools if needed
    if response.tool_calls:
        result = self.executor.execute(tool_call)
        # OBSERVE: Add result to conversation
        conversation.add_tool_result(...)
        continue  # Loop back - agent will think about the result

    # Done! No more tool calls needed
    return AgentResult(...)
```

**Key insight:** The loop enables multi-step reasoning. Agent can:
1. Search for files → see results
2. Read files → see contents
3. Analyze → see analysis
4. Summarize → final answer

#### Step 3: Understand Components (15 min)
- Run: `reveal groqqy/` to see structure
- Read: `groqqy/components/conversation.py` (92 lines)
- Read: `groqqy/components/executor.py` (102 lines)

**Key insight:** Each component has ONE job. Clean separation.

#### Step 4: Watch It Work (10 min)
- Read: `examples/basic_chat.py`
- If you have GROQ_API_KEY, run it!
- Watch multi-step reasoning in logs

**Checkpoint:** You now understand the basic pattern!

---

### Phase 2: Hands-On Exploration (1-2 hours)

**Goal:** Modify the code, add features, break things and fix them

#### Exercise 1: Add a Custom Tool (30 min)

**Difficulty:** Beginner

**Task:** Add a tool that rolls dice

```python
def roll_dice(sides: int = 6) -> str:
    """Roll a dice with specified number of sides."""
    import random
    result = random.randint(1, sides)
    return f"Rolled a {result} on a {sides}-sided dice"

# Use it
from groqqy import Groqqy
bot = Groqqy(tools=[roll_dice])
response, cost = bot.chat("Roll a 20-sided dice")
```

**Learning outcomes:**
- Tools are just Python functions
- Type hints → auto-schema generation
- Docstrings → tool descriptions for LLM

---

#### Exercise 2: Track Iterations (30 min)

**Difficulty:** Beginner

**Task:** Modify Agent to print iteration count after each loop

**File:** `groqqy/agent.py:97-100`

**Hint:** Add a print statement:
```python
while iteration < self.max_iterations:
    iteration += 1
    print(f"[Iteration {iteration}]")  # ← Add this
    response = self._call_llm()
```

**Learning outcomes:**
- How the agentic loop works
- Where to add observability
- How iterations relate to complexity

---

#### Exercise 3: Add Memory (1 hour)

**Difficulty:** Intermediate

**Task:** Create a component that remembers facts across conversations

**Steps:**
1. Create `groqqy/components/memory.py`:
```python
class MemoryManager:
    def __init__(self):
        self.facts = {}

    def store(self, key: str, value: str):
        """Store a fact."""
        self.facts[key] = value

    def recall(self, key: str) -> str:
        """Recall a fact."""
        return self.facts.get(key, "I don't remember that.")

    def list_all(self) -> str:
        """List all stored facts."""
        if not self.facts:
            return "No facts stored."
        return "\n".join(f"{k}: {v}" for k, v in self.facts.items())
```

2. Add memory tool to registry:
```python
registry = ToolRegistry()

def remember(fact: str, detail: str) -> str:
    """Store a fact in memory."""
    memory.store(fact, detail)
    return f"Remembered: {fact} = {detail}"

def recall(fact: str) -> str:
    """Recall a stored fact."""
    return memory.recall(fact)

registry.register_function(remember)
registry.register_function(recall)

bot = Groqqy(tools=registry)
```

3. Test it:
```python
bot.chat("Remember that my favorite color is blue")
bot.reset()
bot.chat("What's my favorite color?")
# Agent should use recall tool!
```

**Learning outcomes:**
- How to create components
- How to add new capabilities
- How tools enable memory

---

### Phase 3: Deep Dive (2-4 hours)

**Goal:** Understand architecture deeply, compare to other frameworks

#### Study 1: Design Patterns (1 hour)

Read [ARCHITECTURE.md](ARCHITECTURE.md) sections:
- Facade Pattern (Bot)
- Strategy Pattern (Provider)
- Registry Pattern (ToolRegistry)
- Composition over Inheritance (Agent)

**Activity:** For each pattern, answer:
1. What problem does it solve?
2. How is it implemented in Groqqy?
3. What would happen without this pattern?

---

#### Study 2: ReAct Paper Mapping (1 hour)

Read the [ReAct paper](https://arxiv.org/abs/2210.03629) (Yao et al., 2022)

**Activity:** Map paper concepts to Groqqy code

| ReAct Concept | Groqqy Code | Line Number |
|---------------|-------------|-------------|
| Thought | `response = self._call_llm()` | agent.py:102 |
| Action | `result = self.executor.execute(tool_call)` | agent.py:123 |
| Observation | `conversation.add_tool_result(...)` | agent.py:126 |
| Termination | `if not response.tool_calls: return` | agent.py:131 |

**Insight:** Groqqy directly implements the ReAct algorithm!

---

#### Study 3: Compare to LangChain (1 hour)

Install LangChain and compare:

**Task:** Implement same agent in both frameworks

**Groqqy:**
```python
from groqqy import Groqqy

def custom_tool(input: str) -> str:
    return f"Processed: {input}"

bot = Groqqy(tools=[custom_tool])
response, cost = bot.chat("Use custom tool")
```

**LangChain:**
```python
from langchain.agents import initialize_agent
from langchain.tools import Tool
from langchain.chat_models import ChatOpenAI

tool = Tool(name="custom", func=lambda x: f"Processed: {x}", ...)
llm = ChatOpenAI()
agent = initialize_agent(tools=[tool], llm=llm, ...)
response = agent.run("Use custom tool")
```

**Discussion questions:**
- Which is more readable?
- Which is more customizable?
- When would you use each?

---

#### Exercise 4: Add Planning Phase (2 hours)

**Difficulty:** Advanced

**Task:** Extend Agent to create a plan before acting

```python
class PlanningAgent(Agent):
    """Agent that plans before executing."""

    def run(self, prompt):
        # Phase 1: Create plan
        plan = self._create_plan(prompt)
        print(f"Plan: {plan}")

        # Phase 2: Execute plan step by step
        results = []
        for step in plan:
            result = super().run(step)
            results.append(result)

        # Phase 3: Synthesize results
        return self._synthesize(results)

    def _create_plan(self, prompt):
        """Use LLM to create step-by-step plan."""
        planning_prompt = f"""
        Break this task into steps:
        {prompt}

        Return a numbered list of steps.
        """
        response = self._call_llm_with_prompt(planning_prompt)
        # Parse response into list of steps
        return steps

    def _synthesize(self, results):
        """Combine results from all steps."""
        # Implementation
        pass
```

**Learning outcomes:**
- How to extend Agent via subclassing
- Multi-phase agentic patterns
- LLM-based planning

---

## 📚 Key Concepts Explained

### Concept 1: Why Multi-Step Reasoning?

**Single-turn assistant:**
```
User: "Find Python files and count their lines"
LLM: "I'll search for *.py files"
→ Done (unhelpful!)
```

**Multi-step agent:**
```
User: "Find Python files and count their lines"

Iteration 1:
  THINK: "I need to search for Python files first"
  ACT: search_files("*.py")
  OBSERVE: "Found: app.py, test.py, main.py"

Iteration 2:
  THINK: "Now I need to read each file to count lines"
  ACT: read_file("app.py"), read_file("test.py"), read_file("main.py")
  OBSERVE: "app.py: 150 lines, test.py: 89 lines, main.py: 50 lines"

Iteration 3:
  THINK: "I have all the data, I'll summarize"
  RESPONSE: "Found 3 Python files with 289 total lines..."
```

**Why it matters:** Complex tasks require chaining tool calls. Single-turn can't do this.

---

### Concept 2: Why Return Errors as Strings?

**Bad (exceptions):**
```python
def read_file(path):
    with open(path) as f:  # ← Raises FileNotFoundError
        return f.read()

# Agent crashes when file doesn't exist!
```

**Good (error strings):**
```python
def read_file(path):
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File {path} not found"  # ← Agent sees this

# Agent can retry or ask user!
```

**Why it matters:** Agents (LLMs) can see errors and adjust strategy. Exceptions break the loop.

---

### Concept 3: Why Max Iterations?

**Without safeguard:**
```python
while True:  # ← Infinite loop!
    response = llm.chat()
    if response.tool_calls:
        execute_tools()
        continue
```

**If LLM gets confused, loop never terminates → $$$ burned**

**With safeguard:**
```python
while iteration < max_iterations:  # ← Safety guard
    response = llm.chat()
    ...

# After max_iterations, return partial result
return AgentResult(response="[Max iterations reached]")
```

**Why it matters:** Production safety. Runaway agents are expensive and dangerous.

---

### Concept 4: Why Composable Components?

**Monolithic (bad):**
```python
class Agent:
    def __init__(self):
        self.messages = []        # Conversation
        self.total_cost = 0       # Cost tracking
        self.tools = {...}        # Tool management
        # 277 lines of mixed concerns!

    def chat(self):
        # Everything in one giant method
        ...
```

**Problem:** Hard to:
- Test (everything coupled)
- Extend (need to edit giant file)
- Understand (too many responsibilities)

**Composable (good):**
```python
class Agent:
    def __init__(self, provider, tools):
        self.conversation = ConversationManager()  # 92 lines, testable
        self.executor = ToolExecutor(tools)        # 102 lines, testable
        self.tracker = CostTracker()               # 72 lines, testable
        self.provider = provider                   # 35 lines interface

    # Agent just orchestrates - 175 lines total
```

**Benefits:**
- Each component <100 lines
- Test independently
- Swap implementations (e.g., DatabaseConversationManager)
- Easy to understand

**Why it matters:** Software engineering principle - compose simple parts into complex systems.

---

## 🎯 Discussion Questions for Classrooms

### Beginner Questions

1. **What is the difference between a chatbot and an agent?**
   - Hint: Can it use tools? Can it plan multiple steps?

2. **Why does the agentic loop continue after executing tools?**
   - Hint: What does the LLM need to see?

3. **What would happen if we removed max_iterations?**
   - Hint: What if the LLM never stops calling tools?

4. **Why do tools return strings instead of raising exceptions?**
   - Hint: How does the LLM recover from errors?

### Intermediate Questions

5. **How would you add a tool that searches the web?**
   - Implementation exercise

6. **How does ToolRegistry enable extensibility?**
   - Compare to hardcoded tools

7. **What's the purpose of the Provider interface?**
   - Why not just call Groq directly?

8. **How would you implement conversation persistence (save/load)?**
   - Which component would you modify?

### Advanced Questions

9. **How would you implement multi-agent collaboration?**
   - Hint: Multiple Agent instances, shared tools?

10. **How would you add streaming responses?**
    - Hint: yield chunks instead of return complete response

11. **Compare Groqqy's architecture to LangGraph. What are the trade-offs?**
    - Discussion: simplicity vs features

12. **How would you implement "reflection" (agent critiques its own output)?**
    - Hint: Another LLM call after generating response?

---

## 🛠️ Project Ideas for Students

### Beginner Projects

**1. Weather Agent**
- Add weather API tool
- Agent answers: "What's the weather in Seattle?"
- Tools: get_weather(city)

**2. File Organizer**
- Add tools: list_files(), move_file(), create_directory()
- Agent organizes downloads folder by file type

**3. Math Tutor**
- Add tools: solve_equation(), explain_concept()
- Agent helps with homework step-by-step

---

### Intermediate Projects

**4. Code Analyzer**
- Tools: read_file(), count_lines(), find_functions(), check_style()
- Agent audits code quality

**5. Research Assistant**
- Tools: search_web(), read_pdf(), summarize()
- Agent researches a topic and creates summary

**6. Task Manager**
- Tools: add_task(), complete_task(), list_tasks()
- Agent manages to-do list via natural language

---

### Advanced Projects

**7. Multi-Agent System**
- Create: ResearchAgent, WritingAgent, EditorAgent
- Collaborate on writing a blog post

**8. Planning Agent**
- Extends Agent with planning phase
- Creates plan → executes → reflects

**9. Learning Agent**
- Stores what it learns in vector database
- Improves over time by recalling past experiences

**10. Autonomous Developer**
- Tools: read_code(), write_code(), run_tests(), commit()
- Agent implements features from specifications

---

## 📊 Framework Comparison Table

**For students choosing which framework to learn:**

| Feature | Groqqy | LangChain | AutoGPT | LangGraph |
|---------|--------|-----------|---------|-----------|
| **Learning Curve** | 2 hours | 2 weeks | 1 week | 1 week |
| **Core LOC** | 1,200 | 50,000+ | 8,000 | 3,000 |
| **Files to read** | 7 | 30+ | 20+ | 15+ |
| **Understandability** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Teaching-friendly** | ✅ Yes | ❌ No | ❌ No | ⚠️ Moderate |
| **Production-ready** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Extensibility** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Customizable** | Very easy | Hard | Moderate | Moderate |
| **Ecosystem** | Small | Huge | Medium | Growing |
| **Community** | Small | Large | Large | Growing |

**Recommendation:**
- **Learn agentic AI fundamentals:** Start with Groqqy
- **Build production systems:** Graduate to LangChain or LangGraph
- **Understand internals:** Groqqy's code is readable, others are complex

---

## 🎓 Syllabus Suggestion (4-week course)

**Course:** Introduction to Agentic AI

### Week 1: Foundations
- Day 1: What are AI agents? (lecture)
- Day 2: ReAct paper discussion
- Day 3: Install Groqqy, run examples
- Day 4: Read agent.py, understand loop
- Day 5: Lab - Add custom tool

### Week 2: Architecture
- Day 1: Component design patterns
- Day 2: Facade, Strategy, Registry patterns
- Day 3: Read ARCHITECTURE.md
- Day 4: Lab - Add memory component
- Day 5: Project proposal due

### Week 3: Advanced Topics
- Day 1: Multi-agent systems
- Day 2: Planning and reflection
- Day 3: RAG (retrieval-augmented generation)
- Day 4: Lab - Extend agent capabilities
- Day 5: Guest lecture - Production AI agents

### Week 4: Projects
- Day 1-4: Work on final project
- Day 5: Project presentations

**Final Project Options:**
- Build domain-specific agent (research, code, customer service)
- Implement planning agent
- Create multi-agent collaboration system
- Compare frameworks (Groqqy vs LangChain)

---

## 📖 Recommended Reading Order

**For self-learners:**

1. **Start here:** [README.md](README.md) - Overview and quick start
2. **Then read:** This file (TEACHING_GUIDE.md) - Learning path
3. **Core code:** `groqqy/agent.py:70-157` - The agentic loop
4. **Deep dive:** [ARCHITECTURE.md](ARCHITECTURE.md) - Component design
5. **Design rationale:** [AGENTIC_ARCHITECTURE_PROPOSAL.md](AGENTIC_ARCHITECTURE_PROPOSAL.md)
6. **Academic:** [ReAct paper](https://arxiv.org/abs/2210.03629)
7. **Compare:** LangChain docs, AutoGPT repo

**Total time:** 6-8 hours to go from zero to understanding agentic AI.

---

## 💡 Teaching Tips for Educators

### Tip 1: Start with the Loop

**Most important code:** `agent.py:97-145` (the while loop)

Don't start with architecture diagrams. Start with:
1. Show the loop
2. Walk through one iteration
3. Show how it chains tools
4. THEN explain components

**Why:** Concrete before abstract.

---

### Tip 2: Live Coding Works

Groqqy is small enough to livecode:

**Example lesson:**
1. Start with empty file
2. Livecode Agent.run() loop
3. Show THINK → ACT → OBSERVE
4. Add logging to show iterations
5. Run it!

**Why:** Students see it being built, not black box.

---

### Tip 3: Break Things

**Exercise:** Remove max_iterations check, show infinite loop

**Exercise:** Make tool raise exception, show agent crashes

**Exercise:** Remove tool_calls check, show it never terminates

**Why:** Breaking things teaches why design decisions matter.

---

### Tip 4: Compare to Real Systems

Show students production examples:
- ChatGPT plugins (tool calling)
- GitHub Copilot Workspace (multi-step)
- Devin (autonomous developer)

**Discussion:** "Which parts of Groqqy do these systems use?"

**Why:** Connects classroom to real world.

---

### Tip 5: Emphasize Trade-offs

**No silver bullets:**
- Groqqy: Simple ↔ Limited features
- LangChain: Feature-rich ↔ Complex
- AutoGPT: Autonomous ↔ Unpredictable

**Discussion:** When would you use each?

**Why:** Critical thinking > memorization.

---

## 🔗 Additional Resources

### Academic Papers

- **ReAct** (Yao et al., 2022): https://arxiv.org/abs/2210.03629
- **Toolformer** (Schick et al., 2023): https://arxiv.org/abs/2302.04761
- **Reflexion** (Shinn et al., 2023): https://arxiv.org/abs/2303.11366

### Production Frameworks

- **LangChain**: https://python.langchain.com/
- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **AutoGPT**: https://github.com/Significant-Gravitas/AutoGPT
- **CrewAI**: https://www.crewai.com/

### Groqqy Resources

- **Source Code**: `groqqy/` directory
- **Examples**: `examples/` directory
- **Tests**: `test_architecture.py`, `test_config_system.py`
- **Docs**: README.md, ARCHITECTURE.md, this file

---

## ✅ Learning Checkpoints

**After Phase 1 (Understanding), you should be able to:**
- [ ] Explain what an agent is vs. a chatbot
- [ ] Draw the THINK → ACT → OBSERVE loop
- [ ] Read agent.py and understand the while loop
- [ ] Identify the 5 components (Agent, Bot, Conversation, Executor, Tracker)

**After Phase 2 (Hands-On), you should be able to:**
- [ ] Add a custom tool
- [ ] Modify agent behavior
- [ ] Create a new component
- [ ] Run examples and interpret logs

**After Phase 3 (Deep Dive), you should be able to:**
- [ ] Explain design patterns used
- [ ] Map ReAct paper to code
- [ ] Compare Groqqy to other frameworks
- [ ] Extend Agent with subclasses

**Mastery level:**
- [ ] Build domain-specific agent from scratch
- [ ] Implement multi-agent collaboration
- [ ] Add planning or reflection
- [ ] Contribute to Groqqy codebase

---

## 🎯 Summary

**Groqqy as teaching kernel:**
- Small enough to understand fully (1,200 LOC)
- Real enough to be useful (production patterns)
- Clear enough to learn from (explicit comments)
- Extensible enough to build on (composable components)

**Perfect for:**
- University courses on AI agents
- Workshops and bootcamps
- Self-directed learning
- Research prototypes

**Not perfect for:**
- Production systems requiring LangChain's ecosystem
- Enterprise features (monitoring, scaling)
- Maximum performance optimization

**The value:** Groqqy teaches fundamentals. Once you understand Groqqy, you can learn any agentic framework.

**Start here → Graduate to production frameworks**

---

**Questions? Ideas? Contributions?**

Open an issue or PR in the Groqqy repo!

**Happy learning!** 🎓🤖
