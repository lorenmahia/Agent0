from buffet_agent import *
import time
import json



with open("symbols.json", "r") as f:
    symbols_data = json.load(f)


def main():
    """This function automated the calling of the buffet agent to perform stock research and analysis.
     It calls buffet agent for a list of Symbols and saves the output to a text file in the current directory.
     It will wait for 60 seconds before each call to avoid rate limiting."""
    
    symbols = symbols_data.get("Symbols", [])
    symbols = [s.strip().upper() for s in symbols if s.strip()]

    for symbol in symbols:
        print(f"Researching {symbol}...")
        result = call_buffet_agent(symbol)
        print(f"Analysis for {symbol} complete. Waiting 60 seconds before next symbol...")
        time.sleep(60)

    pass

if __name__ == "__main__":
    main()