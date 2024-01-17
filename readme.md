**Line Chatbot for Similar Artworks**

This is a Line chatbot designed to help users find similar artworks in a database. This project leverages the Line Messaging API to provide a seamless and interactive experience for art enthusiasts.

**## Table of Contents**

- [ArtBot - Line Chatbot for Similar Artworks](#artbot---fastapi-line-chatbot-for-similar-artworks)
  - [Introduction](#introduction)
  - [Features](#features)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
  - [Usage](#usage)

**## Introduction**

This is a Line chatbot that utilizes an advanced algorithm to find similar artworks in a database based on user input image.

**## Features**

 - Crop Image
 - Find Dominant color
 - find similar artwork

**## Getting Started**

Follow these steps to set up ArtBot and start using it.

**### Prerequisites**

Before you begin, make sure you have the following installed:

- Python 3.x
- [FastAPI](https://fastapi.tiangolo.com/)
- [Uvicorn](https://www.uvicorn.org/)
- Line Developer Account (for API access)
- ngrok

**### Installation**

1. Clone the ArtBot repository:

```bash 
$ git clone https://github.com/PacharaXx/Thesis
$ cd Thesis
```

2. Install Python dependencies:
```bash
$ pip install-r requirements.txt
```

3. Set up your Line Messaging API credentials in the env file.
```
  IP = localhost
  TOKEN = 
  CHANNEL_SECRET = 
  IP_URL = 'https://xxxxxxxxxxxxxxx.ngrok-free.app/'
```
4. Run a Ngrok
```bash
$ ngrok http --domain=xxxxxxxxxxxxx.ngrok-free.app 8080
```

5. Start the server.py
```bash
$ python server.py
```

Now, it should be up and running!

Usage
1. Add ArtBot as a friend on Line.
2. Select menu
3. Send an image
4. Receive similar artworks and explore the world of art!

DEMO
https://github.com/PacharaXx/Thesis/assets/128677831/f9c059bb-ac1f-43fb-b182-38b62c642cc5






