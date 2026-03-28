# 1. Macro Dashboard

## Overview:
This project is a simple dashboard tool to track key macroeconomic indicators such as interest rates, inflation , DXY, and commodity price.

The goal is to provide a centralized view of important macro signals to support investment and economic analysis.

## Features:
	- Interactive dashboard built with Streamlit
	- Track key macro indicators:
  		- Interest rates (Fed)
  		- Inflation (CPI)
  	- USD strength (DXY)
  	- Commodity prices (Gold)
	- Display data in a simple and readable format
	- Desigb for quick marcro monitoring
	- Portfolio allocation support tool

## Tech Stack:
	- Python
	- Streamlit / Matplotlib / Pandas 
	- Cursor IDE
	- Claude Code & Codex

## Challenges & Solutions:
### Issue 1: Data collection
	- Problem: I encountered difficulties when trying to load data directly from the FRED website
	- Solution: I resolved this by manually downloading and cleaning the dataset before importing it as offline data for the initial version

### Issue 2: Code errors and feature improvements
	- Problem: I ran into several issues related to data display and functionality during development
	- Solution: I iteratively debugged the code and made improvements to both the UI and features to ensure the dashboard worked correctly

## AI Usage:
I used AI tools (Claude Code and Codex) inside Cursor to:
	-	Generate initial project structure
	-	Debug errors during development
	-	Explore better ways to organize data and UI

## Future Improvements
	-	Integrate real-time data APIs (e.g., FRED)
	-	Add interactive charts and filters
	-	Expand indicator coverage

## Reflection:
This project helped me connect my interest in macroeconomics with practical technical skills. Instead of building a complex system, I focused on creating a simple and intuitive dashboard that reflects how I analyze macro trends in real life



#2. Multi-platform Dashboard

## Overview:
A cross-platform marketing dashboard that aggregates and analyzes ad performance across Web, Facebook, and TikTok.
It eliminates data silos by centralizing key KPIs (ROAS, ROI, CPA, Conversions) into a single source of truth, with built-in insights for better decision-making

## Features:
	- Multi-platform view: Combine data from Web, Facebook, TikTok
	-	Custom KPI targets: Set ROAS, CPA, and cost assumptions
	-	Creative analytics: View ad visuals alongside performance
	-	Automated insights: Highlight winning & losing channels
	-	Smart alerts: Flag underperforming campaigns
	-	Direct links: Jump to ad managers for quick actions

## Tech Stack:
	- Python
	- Streamlit / Matplotlib / Pandas 
	- Cursor IDE
	- Claude Code & Codex

## Challenges & Solutions:
### Issue 1: ROI Calculation
	- Problem: Ad platforms don’t include operating costs, leading to inaccurate ROI
	- Solution: Added a operation cost rate input to estimate overhead and calculate realistic ROI

### Issue 2: Running Streamlit app
	- Problem: I initially tried to run the Python file directly and encountered a permission error
	- Solution: I fixed this by using the correct Streamlit command: `streamlit run ads_dashboard.py`

## AI Usage:
I used Cursor AI for faster development, refactoring, and UI building

## Future Improvements:
	-	API integrations (Meta, TikTok, GA4)
	-	AI-powered creative analysis
	-	Automated budget optimization
	-	Predictive performance forecasting

## Reflection:
This project focuses on turning data into action—helping marketers not just track performance, but decide what to do next