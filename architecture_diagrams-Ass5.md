# QuantSense: System Architecture Diagrams

This document outlines the operational flow and logical interactions of the QuantSense Stock Tracking Tool using UML-standard Mermaid diagrams.

## 1. Activity Flow (Data Processing)
This flowchart illustrates the step-by-step logic from user input to the final signal generation.

```mermaid
flowchart TD
    Start([Start]) --> Input[User enters Stock Ticker]
    Input --> SuffixCheck{Ticker has .NS/.BO?}
    SuffixCheck -- No --> Append[.NS Suffix Added]
    SuffixCheck -- Yes --> API[Send Request to Flask API]
    Append --> API
    API --> Fetch[Fetch 1Y History via yfinance]
    Fetch --> DataCheck{Data Found?}
    
    DataCheck -- No --> Error[Return 404 Error]
    Error --> DisplayError[Display Error Alert]
    DisplayError --> End([End])
    
    DataCheck -- Yes --> Indicators[Calculate Technical Indicators]
    
    subgraph ScoringEngine [Weighted Scoring Engine]
        direction TB
        Trend[Trend Verification]
        Momentum[Momentum Analysis]
        Timing[Execution Timing]
        Confirmation[Confirmation Layers]
    end
    
    Indicators --> ScoringEngine
    ScoringEngine --> Aggregate[Aggregate Net Confidence Score]
    Aggregate --> Signal[Determine Signal: Buy, Sell, or Hold]
    Signal --> Render[Render Dashboard & 3-Panel Charts]
    Render --> End([End])
```

---

## 2. Sequence Diagram (System Interaction)
This diagram shows the interaction between the User, React Frontend, Flask Backend, and External Data Sources.

```mermaid
sequenceDiagram
    participant User
    participant React as Frontend (React/MUI)
    participant Flask as Backend (Flask)
    participant YF as Yahoo Finance (yfinance)

    User->>React: Selects or Searches Ticker
    React->>Flask: GET /api/stock/<ticker>
    
    activate Flask
    Flask->>YF: Fetch Historical OHLCV Data
    YF-->>Flask: Returns CSV/DataFrame
    
    Note over Flask: Calculate RSI, MACD, SMA, etc.
    Note over Flask: Execute Weighted Scoring Engine
    
    Flask-->>React: Return JSON (Signal, Score, Breakdown, ChartData)
    deactivate Flask
    
    activate React
    React->>React: Update Component State
    React->>Chart: Pass Historical Data to Lightweight Charts
    React->>User: Display Signal Alert & Analysis Breakdown
    deactivate React
```

---

## 3. Component Breakdown
- **User Interface**: React + MUI, handling user input and triggering API calls.
*   **Computation Layer**: Flask engine using `pandas` and `ta` for efficient vector-based calculations.
*   **Data Layer**: Integration with `yfinance` to bypass complex exchange API registrations.
*   **Visualization Layer**: Three independent but synchronized `lightweight-charts` instances.
