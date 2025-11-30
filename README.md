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

