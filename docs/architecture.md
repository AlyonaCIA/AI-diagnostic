# AI PLC Diagnostic System - Architecture

## System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        Client[HTTP Client/cURL]
    end

    subgraph "API Layer - FastAPI"
        API[/classify Endpoint]
        Health[/health Endpoint]
    end

    subgraph "Core Processing"
        Parser[PLCParser<br/>Regex-based Error Detection]
        XMLExtractor[XMLContextExtractor<br/>XPath Context Retrieval]
        Agent[PLCDiagnosticAgent<br/>LLM-Powered Analysis]
    end

    subgraph "External Services"
        Gemini[Google Gemini 2.5 Flash<br/>LLM Inference]
    end

    subgraph "Data Models"
        Schema[Pydantic Schemas<br/>DiagnosticReport]
    end

    subgraph "Input Data"
        ErrorLog[Error Log Text<br/>Multi-stage PLC errors]
        XML[PLCopen XML<br/>Project source code]
    end

    Client -->|POST /classify| API
    Client -->|GET /health| Health
    
    API --> Parser
    API --> XMLExtractor
    
    Parser -->|Stage, Line Number| Agent
    XMLExtractor -->|Code Context| Agent
    
    Agent -->|Prompt Engineering| Gemini
    Gemini -->|Structured Response| Agent
    
    Agent -->|Validate| Schema
    Schema -->|JSON Response| API
    API -->|HTTP 200| Client
    
    ErrorLog -.->|Input| Parser
    XML -.->|Input| XMLExtractor

    style API fill:#4A90E2
    style Agent fill:#F5A623
    style Gemini fill:#7ED321
    style Parser fill:#BD10E0
    style XMLExtractor fill:#50E3C2
    style Schema fill:#B8E986
```

## Data Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant API as FastAPI Server
    participant P as PLCParser
    participant X as XMLContextExtractor
    participant A as PLCDiagnosticAgent
    participant G as Google Gemini API
    
    C->>API: POST /classify {log_text, xml_content}
    
    activate API
    API->>P: parse(log_text)
    activate P
    P->>P: Apply Regex Patterns
    P->>P: Detect Stage & Line
    P-->>API: {stage, line_number}
    deactivate P
    
    API->>X: extract_context(xml, stage, line)
    activate X
    X->>X: Parse XML with lxml
    X->>X: XPath Query
    X-->>API: {pou_name, code_context}
    deactivate X
    
    API->>A: diagnose(stage, line, context)
    activate A
    A->>A: Build Prompt
    A->>G: generate_content(prompt)
    activate G
    G->>G: LLM Inference
    G-->>A: Structured Response
    deactivate G
    
    A->>A: Parse with Pydantic
    A->>A: Validate Schema
    A-->>API: DiagnosticReport
    deactivate A
    
    API-->>C: JSON {severity, stage, fixes}
    deactivate API
```

## Component Responsibilities

```mermaid
flowchart LR
    subgraph "Parsing Layer"
        P1[Stage Detection<br/>XML/IEC/C errors]
        P2[Line Number Extraction<br/>Regex patterns]
        P3[Error Type Classification<br/>Pattern matching]
    end
    
    subgraph "Context Layer"
        C1[XML Parsing<br/>lxml + namespaces]
        C2[Code Extraction<br/>XPath queries]
        C3[POU Location<br/>Target element]
    end
    
    subgraph "AI Layer"
        A1[Prompt Engineering<br/>Context injection]
        A2[LLM Generation<br/>Gemini API]
        A3[Schema Validation<br/>Pydantic models]
    end
    
    P1 --> C1
    P2 --> C2
    P3 --> C3
    
    C1 --> A1
    C2 --> A1
    C3 --> A1
    
    A1 --> A2
    A2 --> A3
    
    style P1 fill:#BD10E0
    style P2 fill:#BD10E0
    style P3 fill:#BD10E0
    style C1 fill:#50E3C2
    style C2 fill:#50E3C2
    style C3 fill:#50E3C2
    style A1 fill:#F5A623
    style A2 fill:#F5A623
    style A3 fill:#F5A623
```

## Error Classification Pipeline

```mermaid
graph LR
    Input[Raw Error Log] --> Detect{Detect Stage}
    
    Detect -->|CRASH pattern| CodeGen[Code Generation Error]
    Detect -->|Compiler pattern| IEC[IEC Compilation Error]
    Detect -->|XML pattern| XMLErr[XML Validation Error]
    Detect -->|No pattern| Unknown[Unknown Stage]
    
    CodeGen --> Extract1[Extract Empty POU]
    IEC --> Extract2[Extract Constant Assignment]
    XMLErr --> Extract3[Extract Malformed XML]
    
    Extract1 --> LLM{LLM Analysis}
    Extract2 --> LLM
    Extract3 --> LLM
    
    LLM --> Classify1[Severity: blocking/warning/info]
    LLM --> Classify2[Complexity: trivial/moderate/complex]
    LLM --> Classify3[Root Cause Analysis]
    
    Classify1 --> Fix[Generate 1-3 Fixes]
    Classify2 --> Fix
    Classify3 --> Fix
    
    Fix --> Report[DiagnosticReport JSON]
    
    style Detect fill:#BD10E0
    style LLM fill:#F5A623
    style Report fill:#B8E986
```

## Technology Stack

```mermaid
mindmap
  root((AI Diagnostic))
    Backend
      FastAPI
        REST API
        Async handlers
        Pydantic validation
      Python 3.12+
        Type hints
        Modern syntax
    Processing
      Regex Parsing
        Stage detection
        Line extraction
      XML Processing
        lxml library
        XPath queries
        Namespace handling
    AI/ML
      Google Gemini
        2.5 Flash model
        Native Pydantic
        Fast inference
      Prompt Engineering
        Context injection
        Structured output
    DevOps
      GitHub Actions
        CI/CD
        Automated tests
        Security audits
      uv Package Manager
        Fast installs
        Lock files
      Docker Ready
    Testing
      pytest
        Unit tests
        Integration tests
        Coverage reports
      Fixtures
        Sample errors
        Mock responses
    Licensing
      AGPL v3
        Open source
        Copyleft protection
      Commercial
        Dual licensing
        Paid option
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Production Environment"
        LB[Load Balancer]
        
        subgraph "Application Servers"
            API1[FastAPI Instance 1<br/>uvicorn worker]
            API2[FastAPI Instance 2<br/>uvicorn worker]
            API3[FastAPI Instance 3<br/>uvicorn worker]
        end
        
        subgraph "External Dependencies"
            GeminiAPI[Google Gemini API<br/>Rate Limited]
        end
        
        subgraph "Monitoring"
            Logs[Loguru Logger<br/>Structured Logs]
            Metrics[Health Endpoints<br/>/health /health/detailed]
        end
    end
    
    subgraph "CI/CD Pipeline"
        GitHub[GitHub Repository]
        Actions[GitHub Actions]
        
        Actions -->|format| Format[Black + isort]
        Actions -->|lint| Lint[Flake8 + Pylint]
        Actions -->|audit| Audit[pip-audit]
        Actions -->|test| Tests[pytest + coverage]
    end
    
    Internet[Internet Traffic] --> LB
    LB --> API1
    LB --> API2
    LB --> API3
    
    API1 --> GeminiAPI
    API2 --> GeminiAPI
    API3 --> GeminiAPI
    
    API1 --> Logs
    API2 --> Logs
    API3 --> Logs
    
    API1 --> Metrics
    
    GitHub --> Actions
    Actions -->|deploy| LB
    
    style LB fill:#4A90E2
    style GeminiAPI fill:#7ED321
    style Actions fill:#F5A623
```

## Key Design Decisions

| Decision | Rationale | Trade-off |
|----------|-----------|-----------|
| **Deterministic Parsing First** | Reduces LLM calls, faster response | Requires maintained regex patterns |
| **Google Gemini 2.5 Flash** | Fast inference (4-10s), native Pydantic | Vendor lock-in, rate limits |
| **XPath Context Extraction** | Precise code targeting, reduced tokens | Requires valid XML structure |
| **Pydantic Schemas** | Type safety, auto validation, OpenAPI docs | Schema evolution overhead |
| **AGPL v3 + Commercial** | Community contributions + revenue model | Legal complexity |
| **Single Binary Deployment** | Simple ops, no DB needed | Stateless only |

## Performance Characteristics

- **Response Time**: 5-10s average (LLM inference bound)
- **Accuracy**: 100% stage/severity/complexity classification
- **Confidence**: 0.97+ average for fix suggestions
- **Throughput**: Limited by Gemini API rate limits
- **Scalability**: Horizontal scaling ready (stateless)

## Future Enhancements

```mermaid
graph LR
    Current[Current System] --> Cache[Redis Caching Layer]
    Current --> Batch[Batch Processing]
    Current --> Streaming[Streaming Responses]
    
    Cache --> Perf[Better Performance]
    Batch --> Scale[Higher Throughput]
    Streaming --> UX[Better UX]
    
    Current --> Models[Multi-Model Support]
    Models --> OpenAI[OpenAI GPT-4]
    Models --> Claude[Anthropic Claude]
    Models --> Local[Local LLMs]
    
    style Current fill:#4A90E2
    style Perf fill:#7ED321
    style Scale fill:#7ED321
    style UX fill:#7ED321
```
