# Customer Experience Analytics for Fintech Apps

**A Real-World Data Engineering Challenge: Scraping, Analyzing, and Visualizing Google Play Store Reviews**

---

## Overview

This project analyzes customer satisfaction with mobile banking apps in Ethiopia by collecting and processing user reviews from the Google Play Store for three banks:

- **Commercial Bank of Ethiopia (CBE)**
- **Bank of Abyssinia (BOA)**
- **Dashen Bank**

As a Data Analyst at Omega Consultancy, your objective is to scrape app reviews, perform sentiment and thematic analysis, store cleaned data in a Postgres database, and deliver actionable insights for improving user experience and app retention.

This project builds upon foundational data skills and introduces:

- Web scraping
- Text preprocessing and NLP
- Database engineering (PostgreSQL)
- Data visualization and reporting

---

## Business Objective

Omega Consultancy supports banks to improve their mobile apps by:

1. Scraping user reviews from the Google Play Store
2. Analyzing sentiment and extracting themes
3. Identifying key satisfaction drivers and pain points
4. Storing cleaned review data in a PostgreSQL database
5. Delivering reports with actionable recommendations

---

## Scenarios

1. **Retaining Users**  
   Analyze whether slow loading times reported by users are widespread and suggest areas for app improvement.

2. **Enhancing Features**  
   Extract desired features (e.g., faster transfers, fingerprint login) and recommend improvements for competitiveness.

3. **Managing Complaints**  
   Cluster and track recurring complaints (e.g., login errors) to guide AI chatbot integration and improve support efficiency.

---

## Dataset Overview

- **Source**: Google Play Store
- **Content**: Review text, rating (1–5 stars), date, bank/app name
- **Minimum Size**: 400 reviews per bank (1,200 total)

---

## Team & Facilitation

- **Facilitators**: Kerod, Mahbubah, Filimon

---

## Key Dates

| Milestone                  | Date & Time (UTC)          |
|-----------------------------|---------------------------|
| Introduction                | Wed, 26 Nov 2025, 10:30 AM |
| Interim Submission          | Sun, 30 Nov 2025, 8:00 PM  |
| Final Submission            | Tue, 02 Dec 2025, 8:00 PM  |

---

## Communication & Support

- **Slack Channel**: `#all-week-2`  
- **Office Hours**: Mon–Fri, 08:00–15:00 UTC  

---

## Learning Objectives

By the end of this project, you will be able to:

- Scrape and preprocess Google Play Store reviews
- Apply NLP techniques for sentiment and thematic analysis
- Design and implement a relational database schema in PostgreSQL
- Derive actionable insights and visualize them for business stakeholders
- Write modular, version-controlled scripts with unit tests
- Present a data-driven report with recommendations for app improvements

---

## Project Workflow

### Task 1: Data Collection & Preprocessing

**Objectives:**

- Scrape reviews using `google-play-scraper`
- Preprocess reviews: remove duplicates, normalize dates, handle missing data
- Save as CSV: `review`, `rating`, `date`, `bank`, `source`

**GitHub Practices:**

- Create a repository with `.gitignore` and `requirements.txt`
- Use branch `task-1` for development
- Commit frequently with meaningful messages

**KPIs:**

- 1,200+ reviews with <5% missing data
- Clean, well-structured CSV
- Organized Git repository

---

### Task 2: Sentiment & Thematic Analysis

**Objectives:**

- Perform sentiment analysis using:
  - `distilbert-base-uncased-finetuned-sst-2-english` or alternatives (`VADER`, `Text
