## The code follows the following MCP Architecture 🧰 ## 
<p align="center"> 
  <img src="arch.png" width=1000 alt="MCP Architecture"/>
</p>

---
## 🗄️ Servers used in the code:
<ol type = "1">
  <li>
    <p>Demo Server (Involves tools like add, sub, predict_age)</p>
  </li>
  <li>
    <p>X Server (send and read tweets on X.com)</p>
  </li>
</ol>

---
## 🔑 Key Requirements ## 
<ul>
  <li>
    <p><b>Login to X.com and and create api key and thereby give R-W permission</b></p>
  </li>
  <li>
    <p><b>Groq API Key</b></p>
  </li> 
</ul>

---
## 🔧 Add below code for Demo Server (server.py)
```bash
# server.py file:
from mcp.server.fastmcp import FastMCP
import os
import sys
import requests

# Create an MCP server
mcp = FastMCP("Demo")

# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# Subtraction tool
@mcp.tool()
def sub(a: int, b: int) -> int:
    """Subtract two numbers"""
    return a - b


# Age Prediction Tool:
@mcp.tool()
def predict_age(name:str)-> int:
   """Predict the age of person by name"""
   response = requests.get(url=f"https://api.agify.io?name={name}")
   return response.json()["age"]


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()

```

---
<p align = "center">
  <i>Please Note: It is a multiserver mcp client | Feel free to use!</i>
</p>

