from agents.agent_post_test_on_jira import run_confluence_agent
from utils.data_utils import DataUtils
from utils.path_utils import data_dir
from config.mcp_config.mcp_config import atlassian_mcp_config

import asyncio

REQUIREMENTS = "requirements.txt"
requirements = DataUtils.read_file(REQUIREMENTS, data_dir)

query = (
    f"""
            ROLE:
            You are a Lead UI/UX Engineer and Business Systems Analyst. 
            Your task is to perform a granular structural audit of a web page to map out its functional 
            components and content hierarchy.

            CONTEXT:
            Your job is to use following URL of the page https://testers.ai/testing/form_accessibility.html. Visit this 
            page and analyse source code of the page. Provide details of web page implementation.

            TASK:
            Your task is to create Design Document of web page. Create Page, page should have title of Web Page body 
            header.
            Break page into logical groups based on web development practices. Analyse body div.content 
            of the web page and based
            on that form Design Document.
            Content of the page should be break into logical parts. Describe each part in document separately.
            Each description should start with sub title of logical part and should contain description of that logical
            part, technical analyses.  
            Page should be placed in Space named DesignDocs. 

            RULES:
            1. Create robust Design Document which will describe web page in the best technical way.
            2. Use technical terminology to describe segments and web page.
            3. Visual Content Hierarchy: List every major section 
                of the page in order of appearance (e.g., Hero Section, 
                Social Proof/Testimonials, Pricing Grid, FAQ). For each section, 
                summarize its primary purpose and key messaging.
            4. Navigation & Interactive Elements: Identify all primary and secondary navigation menus. 
                List all Call-to-Action (CTA) buttons, including their labels, visual prominence, and 
                (if detectable) where they link to.
            5. Form & Data Entry Audit: Locate every form on the page. For each form, list:
                    5.1 Form Purpose: (e.g., Lead Gen, Newsletter, Login).
                    5.2 Input Fields: List every field (e.g., First Name, Email, Dropdown for 'Company Size').
                    5.3 Field Requirements: Note if fields are marked as required or have specific validation patterns.
                    5.5 Submission Type: Identify the 'Submit' button text and any post-submission triggers
                     (like "Thank You" redirects).
            6. Component Inventory: Identify reusable UI components used throughout the page (e.g., Modals,
                 Accordions, Tabbed Interfaces, Image Carousels).
            7. Information Architecture: Map the heading structure (H1 through H4) to show how the 
                information is organized for the user.

            """
)

message = asyncio.run(run_confluence_agent(atlassian_mcp_config, query))



