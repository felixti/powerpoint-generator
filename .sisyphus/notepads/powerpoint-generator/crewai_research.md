# CrewAI Research for Multi-Agent Content Generation

## Executive Summary

CrewAI is a Python framework for orchestrating collaborative AI agent teams. It provides two primary workflow orchestration approaches:
- **Crews**: Structured multi-agent teams with tasks and processes
- **Flows**: Event-driven workflows with state management

Latest version: **v1.9.0** (January 26, 2026)

---

## 1. CrewAI Architecture Overview

### Core Components

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| **Agents** | Autonomous AI workers with roles, goals, and tools | Memory, knowledge sources, LLM configuration, tools |
| **Tasks** | Work units assigned to agents | Context dependencies, expected outputs, delegation support |
| **Crews** | Container for agents and tasks | Sequential/hierarchical processes, planning, collaboration |
| **Flows** | Event-driven orchestration | State management, persistence, resumable workflows |

### Architecture Pattern

```
┌─────────────────────────────────────────────────────────┐
│                   Crew (Orchestrator)               │
│  ┌──────────────┐  ┌──────────────┐              │
│  │   Agent 1    │  │   Agent 2    │  ...        │
│  │  (Researcher) │  │   (Writer)   │              │
│  └──────────────┘  └──────────────┘              │
│         ↓                  ↓                         │
│  ┌──────────────┐  ┌──────────────┐              │
│  │   Task 1     │  │   Task 2     │              │
│  └──────────────┘  └──────────────┘              │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Crew and Agent Definitions

### 2.1 Agent Configuration

#### Direct Python Definition

```python
from crewai import Agent, LLM

# Create an LLM instance
llm = LLM(
    model="openai/gpt-4o",
    temperature=0.7,
    max_tokens=4000
)

# Define agent with configuration
researcher = Agent(
    role="Senior Research Analyst",
    goal="Uncover cutting-edge developments in AI and data science",
    backstory="""You are an expert research analyst with years of experience
    in analyzing emerging technologies. You have a keen eye for detail and
    excel at synthesizing complex information into actionable insights.""",
    llm=llm,
    verbose=True,
    allow_delegation=False,  # Specialized agents typically don't delegate
    max_iter=15,
    max_rpm=10,  # Rate limiting: max requests per minute
    memory=True  # Enable memory for context retention
)
```

#### YAML Configuration (Recommended)

```yaml
# src/my_project/config/agents.yaml
researcher:
  role: >
    Senior Data Researcher
  goal: >
    Uncover cutting-edge developments in {topic}
  backstory: >
    You're a seasoned researcher with a knack for uncovering the latest
    developments in {topic}. Known for your ability to find most relevant
    information and present it in a clear and concise manner.
  verbose: true
  llm: openai/gpt-4o
  max_iter: 15
  allow_delegation: false

writer:
  role: >
    Content Writer
  goal: >
    Create engaging content based on research findings
  backstory: >
    A skilled writer with a passion for technology who transforms
    complex concepts into compelling narratives.
  verbose: true
  llm: openai/gpt-4o
  allow_delegation: true
```

### 2.2 Crew Configuration Patterns

#### Pattern 1: Sequential Process (Simple Linear Workflow)

```python
from crewai import Agent, Crew, Task, Process

# Define agents
researcher = Agent(
    role="Research Specialist",
    goal="Find accurate, up-to-date information",
    allow_delegation=False,
    verbose=True
)

writer = Agent(
    role="Content Writer",
    goal="Create engaging content",
    allow_delegation=True,
    verbose=True
)

# Define tasks with dependencies
research_task = Task(
    description="Research latest developments in quantum computing",
    expected_output="Comprehensive research summary with key findings",
    agent=researcher
)

writing_task = Task(
    description="Write an article based on research findings",
    expected_output="Engaging 800-word article",
    agent=writer,
    context=[research_task]  # Gets research output as context
)

# Create crew with sequential process
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    process=Process.sequential,  # Tasks execute in order
    verbose=True
)

result = crew.kickoff()
```

#### Pattern 2: Hierarchical Process (Manager-Led Coordination)

```python
from crewai import Agent, Crew, Task, Process

# Manager agent coordinates team
manager = Agent(
    role="Project Manager",
    goal="Coordinate team efforts and ensure project success",
    backstory="Experienced project manager skilled at delegation",
    allow_delegation=True,
    verbose=True
)

# Specialist agents (no delegation)
researcher = Agent(
    role="Researcher",
    goal="Provide accurate research and analysis",
    allow_delegation=False,  # Focus on core expertise
    verbose=True
)

writer = Agent(
    role="Writer",
    goal="Create compelling content",
    allow_delegation=False,
    verbose=True
)

# Manager-led task
project_task = Task(
    description="Create a comprehensive market analysis report with recommendations",
    expected_output="Executive summary, detailed analysis, and strategic recommendations",
    agent=manager  # Manager will delegate to specialists
)

# Hierarchical crew
crew = Crew(
    agents=[manager, researcher, writer],
    tasks=[project_task],
    process=Process.hierarchical,  # Manager coordinates everything
    manager_llm="gpt-4o",  # Required for hierarchical
    verbose=True
)

result = crew.kickoff()
```

#### Pattern 3: CrewBase with Decorators (YAML + Python Mix)

```python
from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, task, crew
from typing import List

@CrewBase
class PresentationCrew:
    """AI PowerPoint generation crew"""

    agents: List[Agent]
    tasks: List[Task]

    # Load YAML configs
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def planner(self) -> Agent:
        return Agent(
            config=self.agents_config['planner'],
            verbose=True
        )

    @agent
    def content_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['content_generator'],
            verbose=True
        )

    @task
    def plan_outline(self) -> Task:
        return Task(
            config=self.tasks_config['plan_outline']
        )

    @task
    def generate_content(self) -> Task:
        return Task(
            config=self.tasks_config['generate_content'],
            context=[self.plan_outline()]
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

# Execute
crew = PresentationCrew().crew()
result = crew.kickoff(inputs={"topic": "AI Trends 2026"})
```

---

## 3. Task Delegation Patterns

### 3.1 Agent Collaboration

When `allow_delegation=True`, agents gain two automatic tools:

1. **Delegate Work Tool**: `delegate_work(task, context, coworker)`
2. **Ask Question Tool**: `ask_question(question, context, coworker)`

```python
from crewai import Agent, Crew, Task, Process

# Enable collaboration
researcher = Agent(
    role="Research Specialist",
    goal="Find accurate, up-to-date information",
    backstory="Expert researcher with access to various sources",
    allow_delegation=True,  # 🔑 Enables collaboration tools
    verbose=True
)

writer = Agent(
    role="Content Writer",
    goal="Create engaging content based on research",
    backstory="Skilled writer who transforms research",
    allow_delegation=True,  # 🔑 Enables asking questions
    verbose=True
)

editor = Agent(
    role="Content Editor",
    goal="Ensure content quality and consistency",
    backstory="Experienced editor with attention to detail",
    allow_delegation=True,
    verbose=True
)

# Collaborative task
article_task = Task(
    description="""Write a comprehensive 1000-word article about 'AI in Healthcare'.
    
    Collaborate with your teammates:
    - Researcher: Provide accurate, up-to-date information
    - Writer: Create engaging, well-structured content
    - Editor: Ensure quality and consistency
    
    Work together to produce a polished article.""",
    expected_output="A well-researched, engaging 1000-word article",
    agent=writer  # Writer leads, can delegate to others
)

crew = Crew(
    agents=[researcher, writer, editor],
    tasks=[article_task],
    process=Process.sequential,
    verbose=True
)

result = crew.kickoff()
```

### 3.2 A2A (Agent-to-Agent) Protocol

CrewAI supports remote agent delegation via A2A protocol:

```python
from crewai import Agent, Crew, Task
from crewai.a2a import A2AClientConfig

# Configure agent to delegate to remote A2A agents
coordinator = Agent(
    role="Research Coordinator",
    goal="Coordinate research tasks efficiently",
    backstory="Expert at delegating to specialized research agents",
    llm="gpt-4o",
    a2a=A2AClientConfig(
        endpoint="https://specialist.example.com/.well-known/agent-card.json",
        timeout=120,
        max_turns=10
    )
)

task = Task(
    description="Research latest developments in quantum computing",
    expected_output="Comprehensive research report",
    agent=coordinator
)

crew = Crew(agents=[coordinator], tasks=[task], verbose=True)
result = crew.kickoff()
```

### 3.3 Context Passing Between Tasks

```python
# Task chain with context dependencies
research_task = Task(
    description="Research competitors in AI chatbot space",
    expected_output="Structured data on competitors",
    agent=researcher
)

analysis_task = Task(
    description="Analyze competitive landscape",
    expected_output="SWOT analysis",
    agent=analyst,
    context=[research_task]  # Receives research output
)

strategy_task = Task(
    description="Develop competitive strategy",
    expected_output="Actionable strategy document",
    agent=strategist,
    context=[analysis_task]  # Receives analysis output
)
```

---

## 4. Multi-Agent Orchestration for Content Creation

### 4.1 Complete Content Generation Pipeline

```python
from crewai import Agent, Crew, Task, Process
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from typing import List

# Agent 1: Research Specialist
researcher = Agent(
    role="Market Research Analyst",
    goal="Gather comprehensive information on any topic",
    backstory="""You are an expert researcher with access to web search
    and scraping tools. You excel at finding reliable sources and
    synthesizing information into clear summaries.""",
    tools=[SerperDevTool(), ScrapeWebsiteTool()],
    allow_delegation=False,
    verbose=True
)

# Agent 2: Content Strategist
strategist = Agent(
    role="Content Strategist",
    goal="Develop content outlines and structures",
    backstory="""You specialize in organizing information into
    compelling content structures. You understand audience engagement
    and create outlines that guide readers effectively.""",
    allow_delegation=True,  # Can ask researcher for more info
    verbose=True
)

# Agent 3: Content Writer
writer = Agent(
    role="Technical Content Writer",
    goal="Create engaging, accurate content",
    backstory="""You are a skilled writer who transforms complex
    topics into accessible content. You balance technical accuracy
    with readability for diverse audiences.""",
    allow_delegation=True,  # Can collaborate with others
    verbose=True
)

# Agent 4: Quality Assurance
qa_agent = Agent(
    role="Quality Assurance Specialist",
    goal="Ensure content accuracy, consistency, and quality",
    backstory="""You have a meticulous eye for detail. You verify
    facts, check for consistency, and ensure content meets
    quality standards before publication.""",
    allow_delegation=False,
    verbose=True
)

# Task Pipeline
task1_research = Task(
    description="""Research topic: {topic}.
    
    Gather information on:
    - Current state and trends
    - Key players and innovations
    - Challenges and opportunities
    - Future projections
    
    Provide a comprehensive summary with sources.""",
    expected_output="Research report with structured findings and citations",
    agent=researcher
)

task2_outline = Task(
    description="""Based on research, create a detailed content outline.
    
    Outline should include:
    - Engaging introduction
    - Main sections with key points
    - Supporting data and examples
    - Strong conclusion
    
    Structure should be optimized for reader engagement.""",
    expected_output="Detailed content outline with section descriptions",
    agent=strategist,
    context=[task1_research]  # Uses research as context
)

task3_write = Task(
    description="""Write full article based on outline.
    
    Requirements:
    - Target audience: {audience}
    - Length: {word_count} words
    - Tone: {tone}
    - Include examples and data points
    
    Collaborate with QA agent to ensure accuracy.""",
    expected_output="Complete article ready for review",
    agent=writer,
    context=[task2_outline]  # Uses outline as context
)

task4_review = Task(
    description="""Review article for quality.
    
    Check for:
    - Factual accuracy
    - Clarity and readability
    - Consistency and flow
    - Typos and grammatical errors
    
    Provide corrections and improvement suggestions.""",
    expected_output="Reviewed article with corrections applied",
    agent=qa_agent,
    context=[task3_write]  # Uses draft as context
)

# Create Crew
content_crew = Crew(
    agents=[researcher, strategist, writer, qa_agent],
    tasks=[task1_research, task2_outline, task3_write, task4_review],
    process=Process.sequential,
    verbose=True,
    memory=True,  # Enable learning from past executions
    planning=True  # Enable planning capability
)

# Execute
result = content_crew.kickoff(inputs={
    "topic": "Generative AI in Enterprise",
    "audience": "Business executives",
    "word_count": 1500,
    "tone": "professional"
})

print(f"Final Article:\n{result.raw}")
```

### 4.2 Parallel Content Generation

```python
from crewai import Agent, Crew, Task, Process

# Setup agents
researcher = Agent(role="Researcher", goal="Gather information", ...)
writer = Agent(role="Writer", goal="Create content", ...)

# Define independent tasks that can run in parallel
task_a = Task(description="Research topic A", agent=researcher)
task_b = Task(description="Research topic B", agent=researcher)

# Create crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[task_a, task_b],
    verbose=True
)

# Process multiple topics at once
inputs = [
    {"topic": "AI in Healthcare", "word_count": 1000},
    {"topic": "AI in Finance", "word_count": 1000},
    {"topic": "AI in Manufacturing", "word_count": 1000}
]

# Execute for each input
results = crew.kickoff_for_each(inputs=inputs)

for i, result in enumerate(results):
    print(f"\n=== Article {i+1} ===\n{result.raw}")
```

---

## 5. Agent Role Definition Patterns

### 5.1 Role Types for Content Creation

| Role Type | Goal | Delegation | Tools |
|-----------|------|-------------|--------|
| **Research Specialist** | Gather accurate information | No | Search, Scraping, File tools |
| **Content Strategist** | Plan structure and flow | Yes | None (relies on collaboration) |
| **Content Writer** | Create engaging content | Yes | File tools for saving |
| **Editor/Reviewer** | Quality assurance | No | Grammar/style tools |
| **Coordinator/Manager** | Orchestrate workflow | Yes | Delegation tools |

### 5.2 Role Definition Best Practices

```python
# ✅ GOOD: Specific, complementary roles
researcher = Agent(
    role="Market Research Analyst",
    goal="Analyze market trends and gather data",
    backstory="Expert researcher with 10+ years in market analysis",
    allow_delegation=False,  # Specialists focus on their domain
    ...
)

writer = Agent(
    role="Technical Content Writer",
    goal="Transform technical concepts into engaging articles",
    backstory="Skilled writer who makes complex topics accessible",
    allow_delegation=True,  # Can ask researcher for clarifications
    ...
)

# ❌ AVOID: Overlapping roles
agent1 = Agent(role="Content Creator", goal="Make content", ...)
agent2 = Agent(role="Content Maker", goal="Create stuff", ...)
```

### 5.3 Collaboration Guidelines in Backstories

```python
coordinator = Agent(
    role="Content Lead",
    goal="Orchestrate content production end-to-end",
    backstory="""You lead content creation team and coordinate
    workflows across multiple agents.

    Collaboration guidelines:
    - Delegate research tasks to Market Research Analyst
    - Ask Content Strategist for outline guidance
    - Consult with Quality Assurance for review criteria
    - Only escalate blocking issues to Project Manager
    
    Always ensure content meets audience needs and quality standards.""",
    allow_delegation=True,
    memory=True  # Learn from past projects
)
```

---

## 6. Advanced Features

### 6.1 Memory and Learning

```python
agent = Agent(
    role="Content Writer",
    memory=True,  # Enables short-term, long-term, entity memory
    ...
)

crew = Crew(
    agents=[...],
    tasks=[...],
    memory=True,  # Crew-level memory for learning
    ...
)
```

### 6.2 Planning Capability

```python
crew = Crew(
    agents=[...],
    tasks=[...],
    planning=True,  # AgentPlanner creates task plans
    planning_llm="gpt-4o",  # Separate LLM for planning
    ...
)
```

### 6.3 Streaming Execution

```python
crew = Crew(
    agents=[...],
    tasks=[...],
    stream=True,  # Enable real-time output
    verbose=True
)

# Stream output as it's generated
streaming = crew.kickoff(inputs={"topic": "AI Trends"})
for chunk in streaming:
    print(chunk.content, end="", flush=True)

# Access final result
result = streaming.result
```

### 6.4 Crew Output Access

```python
result = crew.kickoff()

# Different output formats
print(f"Raw: {result.raw}")                    # String
print(f"JSON: {result.json_dict}")              # Dict
print(f"Pydantic: {result.pydantic}")          # BaseModel
print(f"Tasks: {result.tasks_output}")           # List[TaskOutput]
print(f"Tokens: {result.token_usage}")           # Usage metrics
```

---

## 7. Comparison with LangGraph

| Feature | CrewAI | LangGraph |
|----------|---------|-----------|
| **Architecture** | Agent-centric with Crews/Flows | Graph-based state machines |
| **Configuration** | YAML + Python decorators | Python classes with state graphs |
| **Process Types** | Sequential, Hierarchical | Custom graph topologies |
| **Built-in Tools** | Extensive tool ecosystem | Manual tool integration |
| **Delegation** | Built-in `allow_delegation` | Manual implementation required |
| **Learning Curve** | Lower, declarative | Higher, more flexible |
| **Best For** | Structured multi-agent workflows | Complex state-dependent logic |

---

## 8. Recommended Patterns for PowerPoint Generation

```python
from crewai import Agent, Crew, Task, Process

# Agent: Presentation Planner
planner = Agent(
    role="Presentation Strategist",
    goal="Design effective presentation structures",
    backstory="Expert at creating compelling presentation narratives",
    allow_delegation=True,
    tools=[...]
)

# Agent: Content Researcher
researcher = Agent(
    role="Content Researcher",
    goal="Gather accurate information for slides",
    backstory="Meticulous researcher who finds relevant data",
    allow_delegation=False,
    tools=[search_tool, file_tool]
)

# Agent: Slide Writer
writer = Agent(
    role="Slide Content Creator",
    goal="Create engaging slide content",
    backstory="Skilled writer who distills complex topics",
    allow_delegation=True
)

# Agent: Designer
designer = Agent(
    role="Visual Designer",
    goal="Ensure visual appeal and consistency",
    backstory="Design expert focused on UX",
    allow_delegation=False,
    tools=[pptx_tool]
)

# Task Pipeline
plan_task = Task(
    description="Create presentation outline for {topic}",
    expected_output="Slide-by-slide outline",
    agent=planner
)

research_task = Task(
    description="Research content for each slide",
    expected_output="Detailed research for all slides",
    agent=researcher,
    context=[plan_task]
)

content_task = Task(
    description="Write slide content",
    expected_output="Text content for each slide",
    agent=writer,
    context=[research_task]
)

design_task = Task(
    description="Apply visual design to presentation",
    expected_output="Complete PowerPoint file",
    agent=designer,
    context=[content_task],
    output_file="output/presentation.pptx"
)

# Crew
ppt_crew = Crew(
    agents=[planner, researcher, writer, designer],
    tasks=[plan_task, research_task, content_task, design_task],
    process=Process.sequential,
    verbose=True,
    memory=True
)

# Execute
result = ppt_crew.kickoff(inputs={"topic": "AI Trends 2026"})
```

---

## 9. Key Takeaways

1. **Crew vs Flow**: Use Crews for structured agent teams, Flows for event-driven workflows
2. **Process Selection**: Sequential for simple pipelines, Hierarchical for complex coordination
3. **Delegation**: Enable `allow_delegation=True` for coordinators, disable for specialists
4. **Context Passing**: Use `context` parameter to chain task outputs
5. **Memory**: Enable for agents that learn from past interactions
6. **Planning**: Useful for complex tasks that benefit from upfront planning
7. **YAML Config**: Recommended for maintainability, especially for large teams

---

## References

- **Official Documentation**: https://docs.crewai.com
- **GitHub Repository**: https://github.com/crewAIInc/crewAI
- **A2A Protocol**: https://a2a-protocol.org
- **Latest Version**: v1.9.0 (January 26, 2026)
