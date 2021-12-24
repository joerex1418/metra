# metra
A Python wrapper for interacting with the Metra Transit Feeds:  

**MetraGTSF-StaticFeed**  
**MetraGTSF-RealTimeFeed**


## API Wrappers
- StaticFeed
- RealTimeFeed

## API Objects
- Route
- Trip

## Getting Started
```python
import metra

# API Wrappers
live = metra.RealTimeFeed()
static = metra.StaticFeed()

```