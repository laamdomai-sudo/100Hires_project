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
	- Design for quick marcro monitoring
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
	-	Integrate real-time data APIs (e.g., FRED, macro)
	-	Add interactive charts and filters
	-	Expand indicator coverage

## Reflection:
This project helped me connect my interest in macroeconomics with practical technical skills. Instead of building a complex system, I focused on creating a simple and intuitive dashboard that reflects how I analyze macro trends in real life
