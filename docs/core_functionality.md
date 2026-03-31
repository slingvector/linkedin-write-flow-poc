# LinkedIn Write Flow - Core Functionality

This document outlines the core functionalities and technical architecture of the `linkedin-write-flow` automation system.

## Overview
The project is a Python-based automation engine designed to perform write-heavy operations on LinkedIn, such as publishing posts, commenting, and sending direct messages. 

It handles multiple authentication methods simultaneously to bypass the limitations of both the official LinkedIn API and the undocumented Voyager API. The single entry point for all operations is the `WriteFlow` class.

## Core Modules & Functionality

### 1. Authentication (`write_flow/auth.py`)
To handle different capabilities efficiently safely, the system uses a dual-authentication strategy:
- **OAuth 2.0 Client**: Used exclusively for creating and publishing new posts via the official LinkedIn API (`/v2/ugcPosts`). It uses the `authorization_code` flow, dynamically opening a browser for user consent and catching the callback via a temporary local HTTP server. The token is cached in `.oauth_token_cache.json` for subsequent runs.
- **Voyager Client**: Built on top of the `linkedin-api` package, this uses session cookies (`li_at` and `JSESSIONID` from `.env`) to authenticate. It is used for capabilities not fully supported by the official API, specifically commenting and messaging.

### 2. Post Publishing (`write_flow/post.py`)
- **Endpoint**: Official LinkedIn API (`/v2/ugcPosts`).
- **Functionality**: Creates and immediately publishes text posts.
- **Features**: Supports defining the visibility of the post (`PUBLIC` or `CONNECTIONS`). Includes built-in artificial delays (`POST_DELAY_S`) to prevent API rate limiting.

### 3. Commenting (`write_flow/comment.py`)
- **Endpoint**: Voyager API (`/voyager/api/feed/comments`).
- **Functionality**: Automates the process of commenting on specific LinkedIn posts given their URL.
- **Features**:
  - Automatically parses LinkedIn post URLs or URNs to extract the target activity ID.
  - Supports bulk commenting (`comment_bulk`) with configurable delays (`delay_between`) to remain undetected by LinkedIn spam filters.

### 4. Direct Messaging (`write_flow/messaging.py`)
- **Endpoint**: Voyager API.
- **Functionality**: Automates direct messaging with fine-grained targeting.
- **Features**:
  - **Direct Messages**: Send a message to a specific LinkedIn user using their profile URL, vanity ID, or resolved member URN.
  - **Interactors Targeting**: Automatically fetches users who interacted (reacted or commented) with a specific LinkedIn post.
  - **Bulk Messaging**: Sends messages to all interactors of a post with hard caps (`max_recipients`) and strict delays between messages to prevent account flagging.

### 5. Flow Orchestrator (`write_flow/writer.py`)
The `WriteFlow` orchestrator unifies all functionalities under one simple interface. Upon instantiation, it intelligently sets up both the OAuth and Voyager clients.

**Common automated workflows include:**
- Publishing a generated post.
- Engaging via comments on target industry posts.
- Scraping a high-performing post's audience and sending targeted intro messages to reactors and commenters.

## Example Usage
Detailed usage instructions and practical examples linking these targeted functionalities can be found in the root `example.py` file.
