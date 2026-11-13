"""
Base agent architecture for Hưng Phát Multi-Agent Workflow.
Provides unified logging, execution tracking, and artifact persistence.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict
import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s")


class BaseWorkflowAgent(ABC):
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.logger = logging.getLogger(f"Agent.{name}")

    def log(self, message: str, level: str = "info"):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{self.name}] {message}"
        if level == "error":
            self.logger.error(formatted)
        elif level == "warning":
            self.logger.warning(formatted)
        else:
            self.logger.info(formatted)

    @abstractmethod
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the agent's task within the workflow.
        Takes current state, performs processing, and returns state updates.
        """
        pass

