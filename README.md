# Car Sales Agent

## Description

This project is about building an AI Sales agent chatbot that helps customers with inquiries about used cars. The Agent’s goal is to convince customers to schedule a test drive for a car they're interested in.

The Agent utilizes the Gemini function calling feature to translate user queries into Postgres queries. If a customer expresses interest in a particular car, the chatbot guides them through the process of booking a test drive.

## Installation

Clone the repository: <br>
`git clone https://github.com/ritobrotos/car-sales-agent.git`

Navigate to the project directory: <br>
`cd car-sales-agent`

Install the required packages: <br>
`pip install -r requirements.txt`

## High Level Design

Below is the high-level design of the project.

<img width="1053" alt="Screenshot 2024-05-03 at 11 50 46 AM" src="https://github.com/ritobrotos/car-sales-agent/assets/9121431/92e2f56b-d607-4e38-a4fc-2a465546a231">

## Usage

Run the following command to start the chatbot: <br>
`python3 -m streamlit run src/sales_agent/chat_ui.py`

## Language & Libraries

- Language: <br> -- Python
- Libraries: <br>
  -- Langchain <br>
  -- Streamlit
- LLM Used <br>
  -- Google Gemini

## Demo

Project demo can be found here: <br>
https://www.youtube.com/watch?v=7p2fRSqm1PI
