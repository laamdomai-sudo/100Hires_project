# Multi-platform Dashboard

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
