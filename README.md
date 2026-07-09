# Ramp Accounts Payable (AP) Automation

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.9%2B-green.svg)
![Ramp API](https://img.shields.io/badge/API-Ramp_Developer-yellow.svg)

> **A zero-touch automation pipeline that instantly converts vendor-emailed invoices into fully approved, scheduled ACH payments within the Ramp ecosystem.**

---

## 🏗️ Architecture: The 4-Step "Draft-to-Paid" Pipeline

This project leverages the **Ramp Developer API** to bridge the gap between Ramp's email OCR ingestion and the final payment approval process. It replaces manual data entry and UI approvals with a highly resilient, automated background daemon.

### 1. Ingestion (Ramp AI & OCR)
Vendors email PDF invoices directly to the company's designated Ramp AP email address. Ramp's internal AI automatically scans the PDF, extracts the core financial data (Amount, Vendor, Date), and generates a temporary `Ready for review` stub in the **Drafts** tab.

### 2. Polling (Python Daemon)
The `main.py` daemon runs continuously in the background, executing a `schedule` loop every 60 seconds. It polls the dedicated draft endpoint (`GET /developer/v1/bills/drafts`) to download all newly created invoices awaiting review.

### 3. Safety Validation
Before constructing a payment payload, the daemon validates the integrity of the OCR extraction. If Ramp's AI failed to confidently extract the **Vendor ID** or **Invoice Number**, the script safely ignores the draft. This guarantees that only perfect, fully-formed invoices are processed, leaving broken PDFs for manual human review.

### 4. Auto-Approval & Payment (The 2-Track Flow)
The script reformats the validated data and pushes it back to Ramp via the standard Bill endpoint (`POST /developer/v1/bills`). 
*   Because the bill is created via the Developer API, Ramp automatically bypasses the manual approval chain (marking it **Approved**).
*   The payload utilizes `use_default_payment_method: True`, dropping the invoice directly into the **Payment Required** tab.

---

## 👻 Handling "Ghost Drafts" (API Limitation)

**Ramp's Developer API strictly prohibits the deletion or archiving of Draft bills via code.** 

Because the API refuses `DELETE` requests for drafts, the original email draft will remain sitting in the Ramp UI even after the real bill is pushed. To prevent infinite loops or duplicate payments:
1. When the script loops back around, it attempts to process the "Ghost Draft" again.
2. Ramp's internal Duplicate Invoice Checker throws an HTTP `400 Bad Request` because a bill with that exact Vendor and Invoice Number already exists.
3. The daemon cleanly catches this duplicate error, logs `SKIPPING: A bill for this invoice already exists`, and safely ignores the ghost draft on all future runs. 

These ghost drafts pose absolutely no financial risk and can be safely ignored or bulk-deleted in the Ramp UI periodically.

---

## 🚀 Getting Started

### Prerequisites
*   Python 3.9+
*   Ramp Developer API Credentials (Client ID, Client Secret, Scopes: `bills:read`, `bills:write`)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd ramp-automation
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure Environment Variables:
   Create a `.env` file in the root directory and add your Ramp API credentials:
   ```env
   RAMP_CLIENT_ID=your_client_id_here
   RAMP_CLIENT_SECRET=your_client_secret_here
   ```

### Running the Daemon
To start the continuous background worker:
```bash
python main.py
```

---

## 📜 License & Authorship
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Author:** Vamshi Batthula  
**Contact:** batthulavamshi740@gmail.com
