# indicators.py
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod


class TechnicalIndicator(ABC):
    """Abstract base class for technical indicators"""

    def __init__(self, df):
        self.df = df.copy()
        self.traces = []

    @abstractmethod
    def calculate(self):
        """Calculate the indicator values"""
        pass

    @abstractmethod
    def get_traces(self):
        """Get plotly traces for the indicator"""
        pass

    def get_subplot_params(self):
        """Get subplot parameters for the indicator"""
        return {"rows": 1, "show_legend": True}  # Default to main price chart


class MovingAverage(TechnicalIndicator):
    def __init__(self, df, periods=[20, 50, 200]):
        super().__init__(df)
        self.periods = periods

    def calculate(self):
        for period in self.periods:
            self.df[f"MA{period}"] = self.df["Close"].rolling(window=period).mean()
        return self.df

    def get_traces(self):
        colors = [
            "rgba(255, 165, 0, 0.9)",
            "rgba(128, 0, 128, 0.9)",
            "rgba(0, 128, 0, 0.9)",
        ]
        return [
            {
                "type": "scatter",
                "x": self.df.index,
                "y": self.df[f"MA{period}"],
                "name": f"{period}-day MA",
                "line": {"color": color, "width": 1.5},
            }
            for period, color in zip(self.periods, colors)
        ]


class MACD(TechnicalIndicator):
    def __init__(self, df, fast=12, slow=26, signal=9):
        super().__init__(df)
        self.fast = fast
        self.slow = slow
        self.signal = signal

    def calculate(self):
        exp1 = self.df["Close"].ewm(span=self.fast, adjust=False).mean()
        exp2 = self.df["Close"].ewm(span=self.slow, adjust=False).mean()
        self.df["MACD"] = exp1 - exp2
        self.df["Signal"] = self.df["MACD"].ewm(span=self.signal, adjust=False).mean()
        self.df["MACD_Hist"] = self.df["MACD"] - self.df["Signal"]
        return self.df

    def get_traces(self):
        return [
            {
                "type": "scatter",
                "x": self.df.index,
                "y": self.df["MACD"],
                "name": "MACD",
                "line": {"color": "rgb(0, 0, 255)", "width": 1.5},
            },
            {
                "type": "scatter",
                "x": self.df.index,
                "y": self.df["Signal"],
                "name": "Signal",
                "line": {"color": "rgb(255, 165, 0)", "width": 1.5},
            },
            {
                "type": "bar",
                "x": self.df.index,
                "y": self.df["MACD_Hist"],
                "name": "MACD Histogram",
                "marker": {
                    "color": [
                        (
                            "rgba(0, 150, 50, 0.5)"
                            if val >= 0
                            else "rgba(220, 50, 50, 0.5)"
                        )
                        for val in self.df["MACD_Hist"]
                    ]
                },
            },
        ]

    def get_subplot_params(self):
        return {"rows": 3, "show_legend": True}  # Display in third subplot


class RSI(TechnicalIndicator):
    def __init__(self, df, period=14):
        super().__init__(df)
        self.period = period

    def calculate(self):
        delta = self.df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        rs = gain / loss
        self.df["RSI"] = 100 - (100 / (1 + rs))
        return self.df

    def get_traces(self):
        return [
            {
                "type": "scatter",
                "x": self.df.index,
                "y": self.df["RSI"],
                "name": f"RSI ({self.period})",
                "line": {"color": "rgb(75, 0, 130)", "width": 1.5},
            }
        ]

    def get_subplot_params(self):
        return {"rows": 4, "show_legend": True}  # Display in fourth subplot
