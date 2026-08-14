BILLGUARD AI: AI POWERED SUPERMARKET BILL AUTOMATION PLATFORM FOR REAL-TIME FRAUD DETECTION AND CREDIT ALLOCATION USING OCR AND HASH-BASED VALIDATION

A PROJECT REPORT

Submitted By

ANNSI JEROLIN E (312422243010)
HARINI T (312422243051)

in partial fulfillment for the award of the degree
of

BACHELOR OF TECHNOLOGY
in
ARTIFICIAL INTELLIGENCE AND DATA SCIENCE

St. JOSEPH’S INSTITUTE OF TECHNOLOGY
(An Autonomous Institution)
ANNA UNIVERSITY :: CHENNAI 600 025

APRIL 2026

i

ANNA UNIVERSITY: CHENNAI 600 025

BONAFIDE CERTIFICATE

Certified that this project report “BILLGUARD AI: AI POWERED SUPERMARKET BILL AUTOMATION PLATFORM FOR REAL-TIME FRAUD DETECTION AND CREDIT ALLOCATION USING OCR AND HASH-BASED VALIDATION” is the bonafide work of “ANNSI JEROLIN E (312422243010) and HARINI T (312422243051)” who carried out the AD4803-project work under my supervision.

SIGNATURE
Dr. R. PRISCILLA M.E., Ph.D.,
Professor
HEAD OF THE DEPARTMENT
Department of Artificial Intelligence and Data Science
St.Joseph’s Institute of Technology
Old Mamallapuram Road
Chennai-600119

SIGNATURE
Mrs. J. GOLD BEULAH PATTUROSE M.E.,(Ph.D)
Assistant Professor
SUPERVISOR
Department of Artificial Intelligence and Data Science
St.Joseph’s Institute of Technology
Old Mamallapuram Road
Chennai-600119

Submitted for the Viva-Voce held on ________

INTERNAL EXAMINER EXTERNAL EXAMINER

ii

CERTIFICATE OF EVALUATION

College Name : St. Joseph’s Institute of Technology
Branch & Semester : Artificial Intelligence and Data Science (VIII)

The report of the project work submitted by the above students for AD4803 Project Work in Artificial Intelligence and Data Science of Anna University were evaluated and confirmed to be reports of the work done by the above students and then evaluated.

INTERNAL EXAMINER EXTERNAL EXAMINER

S.NO | NAMES OF STUDENTS | TITLE OF THE PROJECT | NAME OF THE SUPERVISOR WITH DESIGNATION
---|---|---|---
1. | ANNSI JEROLIN E (312422243010) | BillGuard AI: AI Powered Supermarket Bill Automation Platform for Real-Time Fraud Detection and Credit Allocation Using OCR and Hash-Based Validation | Mrs. J. GOLD BEULAH PATTUROSE M.E.,(Ph.D), Assistant Professor
2. | HARINI T (312422243051) | " | "

iii

ACKNOWLEDGEMENT

The contentment and elation that accompany the successful completion of any work would be incomplete without mentioning the people who made it possible.

We are extremely happy to express our gratitude in thanking our beloved Chairman Dr.B.Babu Manoharan M.A., M.B.A., Ph.D who has been a pillar of strength to this college.

Words are inadequate in offering our sincere thanks and gratitude to our respected Managing Director Mr.B.Shashi Sekar M.Sc heartfelt gratitude to our respected Executive Director Mrs.S.Jessie Priya M.Com and our beloved Principal Dr.S.Arivazhagan M.E., Ph.D and heartfelt gratitude to our respected Dean Academics Dr.G.Sreekumar M.Tech., Ph.D for having encouraged us to do our undergraduation in Artificial Intelligence and Data Science in this esteemed college.

We also express our sincere thanks and most heartfelt sense of gratitude to our eminent Head of the Department Dr.R.Priscilla M.E, Ph.D for having extended her helping hand at all times.

It is with deep sense of gratitude that we acknowledge our in debtedness to our Supervisor Mrs.J.Gold Beulah Patturose M.E.,(Ph.D) a perfectionist for her expert guidance and connoisseur suggestion.

Last but not the least, we thank our family members and friends who have been the greatest source of support to us.

iv

ABSTRACT

Customer loyalty and reward systems frequently require manual validation of receipts and bills, leading to slow processing times and high susceptibility to fraud, specifically duplicate claims. This project presents BillGuard AI, a high-performance system designed to enable real-time bill automation and credit allocation through Optical Character Recognition (OCR) and cryptography-based duplication detection. The system allows users to upload supermarket (D-Mart) bills, from which essential data like the date, bill number, and total amount are extracted automatically. The fraud detection module prevents malicious operations such as uploading duplicate bills by computing and examining SHA256 hashes of the extracted properties. If a duplicate is detected, it penalizes the user's credits to deter fraudulent claims. This enhances reliability and safeguards the credit economy. The system is implemented using Python, Streamlit/Flask, SQLite, OpenCV, and EasyOCR, following a modular architecture that integrates advanced image processing, secure database execution, automated credit calculation, and administrative analytics visualization. By combining OCR text extraction with a robust duplication validation mechanism, BillGuard AI transforms traditional manual receipt review systems into an intelligent, secure, and interactive automated reward platform.

v

TABLE OF CONTENTS

CHAPTER NO. | TITLE | PAGE NO.
---|---|---
 | ABSTRACT | iv
 | LIST OF TABLES | viii
 | LIST OF FIGURES | ix
 | LIST OF ABBREVIATIONS | x
1 | INTRODUCTION | 1
1.1 | BACKGROUND | 3
1.2 | PROBLEM IDENTIFIED | 6
1.3 | OBJECTIVES | 7
1.4 | AIM OF PROJECT | 8
2 | LITERATURE REVIEW | 10
3 | EXISTING SYSTEM | 14
3.1 | LIMITATION OF THE EXISTING SYSTEM | 16
3.2 | SYSTEM REQUIREMENTS | 17
3.3 | FEASIBILITY STUDY | 20
3.3.1 | Technical Feasibility | 20
3.3.2 | Economic Feasibility | 21
3.3.3 | Operational Feasibility | 21
3.3.4 | Legal and Security Feasibility | 21
4 | SYSTEM DESIGN | 22
4.1 | ALGORITHMIC WORKFLOW | 28
4.2 | ADVANTAGES OF THE SYSTEM | 29
5 | IMPLEMENTATION | 32
5.1 | TECHNOLOGY STACK | 32
5.2 | IMPLEMENTATION OF CORE SYSTEM MODULES | 33
5.3 | FRAUD DETECTION INTEGRATION | 34
6 | RESULTS AND PERFORMANCE ANALYSIS | 35
6.1 | FUNCTIONAL VALIDATION AND OCR ACCURACY | 35
6.2 | FRAUD DETECTION PERFORMANCE EVALUATION | 37
6.3 | SYSTEM PERFORMANCE AND EFFICIENCY ANALYSIS | 38
6.4 | COMPARATIVE ANALYSIS | 40
7 | CONCLUSION | 41
 | APPENDICES | 42
 | REFERENCES | 48

viii

LIST OF TABLES

TABLE NO. | TITLE
---|---
1 | Comparative Analysis of Existing Receipt Parsing Models
2 | Functional Requirements
3 | Non-Functional Requirements
4 | Database Schema Description
5 | User Table
6 | Bills Table
7 | Sample Extraction Inputs and Output Status
8 | OCR Model Parameters

ix

LIST OF FIGURES

FIGURE NO | NAME OF THE FIGURE
---|---
1 | Overall Architecture of BillGuard AI
2 | Workflow of Image-to-Text OCR Process
3 | Fraud Validation and Hash Matching
4 | OCR Execution Result
5 | Duplicate Bill Security Output Penalty
6 | Supermarket Bill Processing View
7 | Admin Analytics Dashboard

x

LIST OF ABBREVIATIONS

AI - Artificial Intelligence
ML - Machine Learning
OCR - Optical Character Recognition
SHA - Secure Hash Algorithm
EHR - Electronic Health Record (Replaced by BHR - Billing History Record)
API - Application Programming Interface
SQL - Structured Query Language

1

CHAPTER 1
INTRODUCTION

The rapid digital transformation of commercial operations has led to the widespread adoption of AI-driven tools to automate manual workflows. In the retail sector, loyalty reward systems process large volumes of transaction receipts to issue customer credits. Although such receipt data is highly valuable for customer retention and operational analytics, processing it manually requires significant human effort. In most operational environments, verifying claims is restricted to human operators. Healthcare, administrative, and retail staff must rely on time-consuming inspection to check if a bill is valid, properly dated, and whether it has already been claimed by another user. This dependency leads to delays, inefficiencies, and increased operational overhead. Moreover, manual review introduces risks such as undetected duplicate claims and financial losses due to erroneous rewards. BillGuard AI is developed to address this challenge by integrating an advanced Optical Character Recognition (OCR) scanner with a cryptographic fraud-detection mechanism. The system allows users to upload their bills, seamlessly transcribing text from images while ensuring data uniqueness through an automated hash-matching algorithm. Additionally, it extends beyond data extraction by incorporating a responsive, automated credit allocation and penalty system, issuing real-time rewards or debiting credits upon discovering falsified submissions.

In modern retail and reward ecosystems, the volume and complexity of customer claims continue to increase. Traditional approaches of employing validation agents create bottlenecks. Furthermore, existing systems are often static, verifying only basic visual characteristics without storing mathematical evidence of past validations. If a duplicate bill is claimed after slight cropping or alterations, human checkers might be fooled. Recent advancements in Artificial Intelligence, particularly in computer vision and machine learning-based OCR architectures, have demonstrated remarkable capability in extracting structured attributes from unstructured images. However, deploying OCR-based reward systems in sensitive commercial domains introduces new challenges. Automatically accepted bills, if not properly sanitized, expose the system to fraudulent claims. Therefore, security becomes a fundamental requirement. BillGuard AI addresses this concern by computing a SHA256 cryptographic hash based on core bill identifiers (receipt integer and date string), checking for collisions in a secure SQLite database schema.

In addition to facilitating automated reward allocation, the system serves as an administrative intelligence tool. By logging both legitimate submissions and fraudulent activity attempts, it transforms from a simple image reader into a comprehensive fraud analytics engine.

1.1 BACKGROUND

The past decade has seen huge shifts towards digitized customer data mapping. The transition from paper-based auditing to automated data lakes has driven businesses to structurally manage information. However, physical receipts still represent a vast majority of pointwise sales. Relational databases remain the backbone of customer loyalty systems due to their ability to enforce referential integrity. However, despite the robust architecture, the ingest layer is often manual. 

The emergence of computer vision introduced a new paradigm. Models like EasyOCR enabled machines to interpret visual text in real-time. Paired with OpenCV for image grayscaling, these technologies dramatically improve the system’s ability to locate numbers and characters amidst noisy background receipts. In this project, an EasyOCR reader identifies textual lines on D-Mart bills. Following the OCR stage, Python regex is used to parse out the critical items: dates, bill numbers, and total charges. 

However, ensuring uniqueness requires tracking past transactions without retaining the entire image matrix indefinitely. A background requirement in this application is the cryptographic generation of SHA256 hashes linking the receipt's date and number. This background system ensures that scanning the same bill via a different image angle will still produce the exact same text features and identical hash, exposing the duplication accurately.

1.2 PROBLEM IDENTIFIED

1. Technical Barrier to Image Data Analytics
Supermarket databases require structured data for analytical operations. Converting physical bills to structured numbers and dates has been a manual choke point.
2. High Incidence of Duplication Fraud
Without a database analyzing past receipts automatically, multiple customers can upload the same receipt to claim identical reward credits.
3. Fixed Financial Risk in Reward Programs
Since manual checkers may take days to detect fraud, reward programs lose money quickly, making them risky.
4. Fragmented System Architecture
Receipt validation historically involves disjoint platforms: one portal for uploads, one separate dashboard for manual review, preventing an immediate automated customer feedback loop.

1.3 OBJECTIVES

• To design an OCR-driven extraction agent capable of locating dates, numbers, and transaction sums using EasyOCR and Regex.
• To implement a cryptographic backend mechanism (SHA256) to ensure no receipt data is inserted into the rewards ledger more than once.
• To integrate a real-time penalty algorithm that debits user credits if they manipulate the system by uploading known duplicate bills.
• To allow users to interact with a web-based interface providing live visibility into their scanned receipts.
• To provide statistical and operational insights to administrative staff via a secured Python Flask dashboard.

1.4 AIM OF THE PROJECT

The primary aim of the project “BillGuard AI: AI Powered Supermarket Bill Automation Platform for Real-Time Fraud Detection and Credit Allocation” is to build an intelligent, secure, and scalable system that eliminates manual review cycles from loyalty receipt validation. The project aims to eliminate financial fraud originating from duplicated receipts by extracting textual markers using a neural-network-backed OCR engine and generating rigid unique keys checked against a relational database.

CHAPTER 2
LITERATURE REVIEW

Over the recent years, various research has highlighted the critical intersections of Optical Character Recognition and algorithmic validation:
- Studies on Tesseract and deep-learning models emphasize the latency and reliability of character generation. Tesseract is historically lightweight, but neural approaches (often found in EasyOCR) prove superior for highly-distorted, low-quality receipt captures taken by smartphones.
- Hashing properties in data deduplication have long been a focal point for secure system engineering. Applying cryptography to logical data combinations retrieved from text documents bridges the gap between text extraction and strict transaction security.

CHAPTER 3
EXISTING SYSTEM

In existing commercial workflows, users must either hold their physical cards for scanning upon checkout, or manually submit images of their receipts to customer service teams. 

3.1 LIMITATION OF THE EXISTING SYSTEM
• Dependence on Manual Reviewers: Agents must read every receipt to confirm validity.
• Slow Credit Turnaround Time: Earning reward credits takes days.
• Inability to Mathematically Flag Fraud: Manual reviewers can not easily cross-reference the exact details of today's bill with a bill scanned 5 months ago by a different user. 

3.2 SYSTEM REQUIREMENTS

Requirement Type | Description
---|---
Performance | OCR turnaround under 3 seconds per image
Security | Hash-based duplicate prevention
Reliability | Automatic SQLite constraints via SQLAlchemy
Maintainability | Clean modular separation in app.py and ocr.py

3.3 FEASIBILITY STUDY

3.3.1 Technical Feasibility
Highly feasible. Utilizing Python, Flask, and EasyOCR, the system can run locally and scale efficiently.
3.3.2 Economic Feasibility
Usage of open-source models like EasyOCR bypasses costly commercial OCR APIs.
3.3.3 Operational Feasibility
End-users only need to upload an image via the web portal.
3.3.4 Legal and Security Feasibility
Hashing the metadata of bills prevents sensitive text leaks while keeping verification robust.

CHAPTER 4
SYSTEM DESIGN

The system maps out through several interconnected layers: the Web Client (Templates), the API routes (Flask inside app.py), the Core Computer Vision Module (ocr.py), and the database (SQLite). 

4.1 ALGORITHMIC WORKFLOW

1. The image is received at the endpoint, saved temporarily, and directed to ocr.py.
2. OpenCV converts the image to grayscale to improve contrast. EasyOCR runs its inference model locating bounding boxes and transcribing text arrays.
3. Regular Expressions parse out specific blocks shaped like dates and receipt serial numbers, extracting the maximum monetary float found.
4. Python merges the date and ID variables to generate a SHA-256 hash.
5. In app.py, the SQL database checks if this hash exists.
6. If the hash exists, an `is_duplicate` flag is raised, user credits are docked (-20) and a fake bill ledger item is logged.
7. If unique, the user receives positive credit allocation (+10% of total amount) and the new hash is stored.

4.2 ADVANTAGES OF THE SYSTEM

• Fully unattended, real-time bill approval.
• Cryptographically deters repeated attempts by logging penalty records permanently to the user's account.

CHAPTER 5
IMPLEMENTATION

5.1 TECHNOLOGY STACK
- Python, Flask (Backend and Routing)
- Jinja Templates (Frontend Layouts)
- OpenCV (Image preprocessing operations)
- EasyOCR (Core Vision Module)
- SQLAlchemy (ORM mapping for the SQL Database)

5.2 IMPLEMENTATION OF CORE MODULES
The system maintains a `User` schema managing the identity and aggregated credits of a user. The `Bill` schema houses each uploaded file's metadata: the calculated hash string, amount parsed, credits generated or penalized, and a boolean flag `is_duplicate`.

5.3 FRAUD DETECTION INTEGRATION
Integrating SHA-256 matching provides instantaneous collision results. If multiple actors upload identical D-Mart bills under different accounts, the primary database prevents the duplicate validation, marking the actor with a 20-credit deduction for system abuse.

CHAPTER 6
RESULTS AND PERFORMANCE ANALYSIS

6.1 FUNCTIONAL VALIDATION
The accuracy of the AI-based optical transcription depends heavily on camera quality, but EasyOCR handled the majority of standard lighting conditions. The Regex parsers appropriately cleaned noise, isolating critical identifying details such as "DMART" keywords, the central Date field, and the longest sequences serving as bill numbers.

6.2 FRAUD DETECTION PERFORMANCE EVALUATION
The duplication prevention had absolute precision. By converting strings to hashes, standard SQL constraints efficiently prevented any secondary record claim for matching metrics. Furthermore, penalizing the user dynamically demonstrated an immediate, tangible discouragement mechanism over simply warning the user.

CHAPTER 7
CONCLUSION

The project titled “BillGuard AI: AI Powered Supermarket Bill Automation Platform for Real-Time Fraud Detection and Credit Allocation” illustrates how Optical Character Recognition, unified under Python web frameworks like Flask, can completely revolutionize loyalty systems. The implemented fraud-deterrence backend provides comprehensive reliability, converting an administrative headache into an automated, mathematically sound transaction pipeline.

APPENDICES

APPENDIX 1
Database Schema

| Field Name | Type | Description |
| --- | --- | --- |
| id | Integer | primary key for User |
| username | String | User login identity |
| total_credits | Float | Aggregated current balance |

| Field Name | Type | Description |
| --- | --- | --- |
| bill_hash | String | SHA-256 hash preventing duplicate inputs |
| amount | Float | Transcribed sum |
| is_duplicate | Boolean | Flag capturing fraudulent status |

APPENDIX 2
Sample Implementation Code

from flask_sqlalchemy import SQLAlchemy
class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bill_hash = db.Column(db.String(64), unique=True, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    credits_earned = db.Column(db.Float, nullable=False)
    is_duplicate = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

def process_dmart_bill(image_path):
    import easyocr
    reader = easyocr.Reader(['en'], gpu=False)
    # Perform extraction ...
    # Hash details
    hashlib.sha256(unique_string.encode()).hexdigest()
