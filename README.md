<div align="center">
  <h1>⚡ Ramp Draft-to-Paid Pipeline</h1>
  <p><b>A highly resilient, zero-touch Accounts Payable automation daemon for Ramp.</b></p>
  
  <a href="https://github.com/Vamshi868876/ramp-draft-to-paid-pipeline/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="License">
  </a>
  <a href="https://python.org">
    <img src="https://img.shields.io/badge/Python-3.9+-green.svg?style=for-the-badge&logo=python" alt="Python">
  </a>
  <a href="https://ramp.com">
    <img src="https://img.shields.io/badge/API-Ramp_Developer-yellow.svg?style=for-the-badge&logo=api" alt="Ramp API">
  </a>
</div>

<br>

> **The Problem:** Ramp's AI successfully extracts OCR data from emailed invoices but leaves them trapped as `Ready for review` drafts. Ramp's API actively blocks developers from automating the approval of these drafts.
> 
> **The Solution:** This pipeline bypasses the UI restriction by polling for new drafts, safely validating the AI's OCR extraction, and programmatically constructing **brand new, auto-approved bills** using the exact extracted data—achieving 100% hands-free AP automation.

---

## 🏗️ Architecture & Flowchart

The system operates as an infinite background daemon (`main.py`) running a strict 60-second polling cycle. It implements a resilient **2-Track Flow** to gracefully handle Ramp's internal Duplicate Invoice checking.

```mermaid
graph TD
    %% Styling
    classDef external fill:#f9f9f9,stroke:#333,stroke-width:2px;
    classDef ramp fill:#f4f4c7,stroke:#c4a000,stroke-width:2px;
    classDef daemon fill:#d6e4ff,stroke:#1890ff,stroke-width:2px;
    classDef final fill:#e6f7ff,stroke:#52c41a,stroke-width:2px;
    classDef error fill:#fff1f0,stroke:#f5222d,stroke-width:2px;

    %% Nodes
    A[Vendor emails PDF Invoice]:::external
    B[Ramp OCR Engine Extracts Data]:::ramp
    C[(Ramp Drafts Tab: 'Ready for review')]:::ramp
    
    D{Python Daemon Polling<br/>Every 60s}:::daemon
    E{OCR Validation Check}:::daemon
    
    F[Skip Draft <br> Human Review Required]:::error
    G[Construct API Payload]:::daemon
    
    H[POST /developer/v1/bills]:::ramp
    
    I{Duplicate Invoice Check}:::ramp
    J[Skip Ghost Draft<br>No Duplicate Payout]:::error
    
    K[Bill Auto-Approved]:::final
    L[(Payment Required Tab)]:::final

    %% Edges
    A -->|Inbound Email| B
    B -->|Generates Stub| C
    C -->|GET /bills/drafts| D
    
    D -->|New Draft Found| E
    E -->|Missing Vendor/Invoice| F
    E -->|Valid Extraction| G
    
    G --> H
    H --> I
    
    I -->|Bill Already Exists| J
    I -->|Unique Invoice| K
    K --> L
```

---

## ✨ Core Features

*   🤖 **Zero-Touch Processing:** Vendors email invoices, and they instantly appear in your "Payment Required" queue without a single human click.
*   🛡️ **OCR Validation Layer:** If Ramp's native AI fails to confidently read an invoice number or vendor ID, the daemon safely skips the invoice to prevent malformed API requests.
*   👻 **Ghost Draft Resolution:** Ramp's API blocks the deletion of email drafts (`405 Method Not Allowed`). The daemon circumvents this by catching HTTP `400 Bad Request` duplicate errors and safely ignoring historical "ghost" drafts without crashing.
*   🔄 **Resilient Polling:** Uses the lightweight `schedule` library to manage API limits and ensure continuous background operation without memory leaks.

---

## 🚀 Getting Started

### Prerequisites
*   Python 3.9+
*   Ramp Developer API Credentials (Client ID, Client Secret)
*   OAuth Scopes: `bills:read`, `bills:write`

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Vamshi868876/ramp-draft-to-paid-pipeline.git
   cd ramp-draft-to-paid-pipeline
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Create a `.env` file in the root directory and add your Ramp API credentials:
   ```env
   RAMP_CLIENT_ID=your_client_id_here
   RAMP_CLIENT_SECRET=your_client_secret_here
   ```

### Running the Daemon
To start the continuous background worker, simply execute:
```bash
python main.py
```
The script will authenticate, scan the `/drafts` endpoint, and begin processing in an infinite 60-second loop.

---

## 📜 License & Authorship

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Architect / Author:** Vamshi Batthula  
**Contact:** batthulavamshi740@gmail.com
