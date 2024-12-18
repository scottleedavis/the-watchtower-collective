import google.generativeai as genai
import os
import time
from typing import List

# Placeholder for video "frames"
VIDEO_FRAMES = [
    "Frame 1: People walking normally.",
    "Frame 2: One person wearing a mask.",
    "Frame 3: A door is opened forcefully.",
    "Frame 4: A person is running.",
    "Frame 5: The scene is quiet.",
    "Frame 6: A server rack is shown.",
    "Frame 7: A person is typing on a keyboard very fast.",
    "Frame 8: An old Windows screen with AD login prompt is shown.",
    "Frame 9: A new modern SAML login page is shown",
    "Frame 10: A user is training an AI model. ",
    "Frame 11: An AI model is misidentifying people"
]


#Agent Base Class
class SecurityAgent:
    def __init__(self, name, personality, focus):
        self.name = name
        self.personality = personality
        self.focus = focus
        self.analysis = []

    def process_frame(self, frame):
        raise NotImplementedError("Subclasses must implement process_frame method.")

    def analyze_video(self, video_frames):
        for frame in video_frames:
            analysis_output = self.process_frame(frame)
            if analysis_output:
                self.analysis.append(f"Frame: {frame}\nAnalysis: {analysis_output}")

    def report(self):
        print(f"\n--- Agent: {self.name} Report ---")
        print(f"Personality: {self.personality}")
        print(f"Focus: {self.focus}")
        if self.analysis:
             for item in self.analysis:
                print(item)
        else:
             print("No anomalies or relevant information found.")

class GeminiAgent(SecurityAgent):
  def __init__(self, name, personality, focus, api_key):
    super().__init__(name, personality, focus)
    self.api_key = api_key

    genai.configure(api_key=self.api_key)
    self.model = genai.GenerativeModel('gemini-pro')

  def process_frame(self, frame):
      prompt = f"I am {self.name}, and my job is {self.focus}. I need to watch a security video feed. Here is a video frame: {frame}. Given the information in this frame, and your knowledge of typical security incident causes, what should be considered?  Provide a brief summary of what you find relevant based on my role, or return `None` if there is nothing relevant."

      response = self.model.generate_content(prompt)
      analysis = response.text.strip()

      if "None" in analysis:
           return None
      else:
           return analysis

# Concrete Agent Implementations using Gemini
class SecOpsAgent(GeminiAgent):
    def __init__(self, api_key):
      super().__init__(
          "SecOps",
         "Vigilant, focused on threats and vulnerabilities, detail-oriented, slightly cynical.",
         "Identifies potential security breaches, unusual activity patterns, and deviations from established policies.",
         api_key
      )

class DevOpsAgent(GeminiAgent):
    def __init__(self, api_key):
      super().__init__(
        "DevOps",
        "Practical, proactive, solution-oriented, loves automation, and impatient with slow processes.",
        "Looks for operational issues, performance bottlenecks, and potential system instabilities.",
        api_key
      )

class CloudSecAgent(GeminiAgent):
    def __init__(self, api_key):
      super().__init__(
        "CloudSec",
         "Observant, data-driven, likes patterns, focused on compliance.",
        "Evaluates cloud resource usage, looks for compliance violations, and identifies anomalies within cloud services.",
        api_key
      )

class AISecAgent(GeminiAgent):
    def __init__(self, api_key):
      super().__init__(
        "AISec",
         "Curious, analytical, looks for trends, and hyperfocuses on things.",
        "Monitors user behavior patterns, identify anomalies in model usage, and detects potential adversarial attacks on AI systems.",
        api_key
      )

class ArchitectAgent(GeminiAgent):
    def __init__(self, api_key):
        super().__init__(
            "Architect",
             "Strategic, visionary, decisive, no-nonsense, frustrated with repetitive mistakes.",
           "Identifies systemic weaknesses, enforces best practices, designs resilient systems, and pushes for architectural changes to prevent future incidents.",
            api_key
        )

def main():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("Please set the GOOGLE_API_KEY environment variable.")

    agents = [
        SecOpsAgent(api_key),
        DevOpsAgent(api_key),
        CloudSecAgent(api_key),
        AISecAgent(api_key),
        ArchitectAgent(api_key),
    ]

    print("--- Starting Video Analysis ---")

    for agent in agents:
       agent.analyze_video(VIDEO_FRAMES)
       agent.report()

    print("--- Video Analysis Completed ---")

if __name__ == "__main__":
    main()
