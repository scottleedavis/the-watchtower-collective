# The Watchtower Collective

## Description

The Watchtower Collective is a proof-of-concept project demonstrating a multi-agent security system. This system employs specialized AI-powered agents, each with a unique security focus, to simultaneously analyze a shared video stream of various security tools. By providing a layered approach and multiple perspectives, it aims to enhance threat detection and security awareness.

This system simulates a security operations center (SOC) where diverse security expertise is applied to a single video source - typically a screen-share of various tools (CLI, video monitor, SIEM, etc).  These agents act as a "threat-aware panel",  collectively analyzing the stream to identify incidents and anomalies.

## Key Features

*   **Multi-Agent System:** Leverages the power of collaborative AI agents to analyze video data.
*   **Specialized Agents:** Each agent possesses a unique focus and personality, mimicking different security roles (SecOps, DevOps, CloudSec, AI/ML Security, Architect).
*   **Simulated Video Analysis:** Processes "video frames" (currently represented as text for simplicity) of security tools in a shared stream.
*   **Gemini API Integration:** Utilizes Google's Gemini API (or any other compatible LLM) for intelligent analysis.
*   **Modular Design:** Easily extensible to incorporate additional security agents or alternative video analysis models.
*   **Output Reporting:** Provides individual analysis reports for each agent, showcasing diverse security perspectives.
*   **Simulated Screen Share:** The video feed is a screen share of various security tools.

## Agents

The following security agents are included:

*   **SecOps:** Vigilant, focused on threats and vulnerabilities, detail-oriented, slightly cynical. Identifies potential security breaches, unusual activity patterns, and deviations from established policies.
*   **DevOps:** Practical, proactive, solution-oriented, loves automation, and impatient with slow processes. Looks for operational issues, performance bottlenecks, and potential system instabilities.
*   **CloudSec:** Observant, data-driven, likes patterns, focused on compliance. Evaluates cloud resource usage, looks for compliance violations, and identifies anomalies within cloud services.
*   **AISec:** Curious, analytical, looks for trends, and hyperfocuses on things. Monitors user behavior patterns, identifies anomalies in model usage, and detects potential adversarial attacks on AI systems.
*    **Architect:** Strategic, visionary, decisive, no-nonsense, frustrated with repetitive mistakes. Identifies systemic weaknesses, enforces best practices, designs resilient systems, and pushes for architectural changes to prevent future incidents.

## Getting Started

### Prerequisites

*   Python 3.6+
*   Google Gemini API Key (set as an environment variable: `GOOGLE_API_KEY`)
*   `google-generativeai` library

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/scottleedavis/the-watchtower-collective.git
    cd the-watchtower-collective
    ```
2.  Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

### Usage

1.  Set your `GOOGLE_API_KEY` environment variable:
    ```bash
    export GOOGLE_API_KEY="YOUR_API_KEY"
    ```
    (or configure it in an `.env` file)
2.  Run the `main.py` script:
    ```bash
    python main.py
    ```

   The application will simulate the video analysis and show the output of each agent.

## Example Output
content_copy
Use code with caution.
Markdown

--- Starting Video Analysis ---

--- Agent: SecOps Report ---
Personality: Vigilant, focused on threats and vulnerabilities, detail-oriented, slightly cynical.
Focus: Identifies potential security breaches, unusual activity patterns, and deviations from established policies.
Frame: Frame 2: One person wearing a mask.
Analysis: The person wearing a mask is suspicious and could be a security threat.
Frame: Frame 3: A door is opened forcefully.
Analysis: The forced opening of the door is a potential breach.
Frame: Frame 4: A person is running.
Analysis: The person running could be attempting to flee a crime.

--- Agent: DevOps Report ---
Personality: Practical, proactive, solution-oriented, loves automation, and impatient with slow processes.
Focus: Looks for operational issues, performance bottlenecks, and potential system instabilities.
Frame: Frame 3: A door is opened forcefully.
Analysis: The forced opening of the door may indicate a system or security problem.
Frame: Frame 6: A server rack is shown.
Analysis: The server rack's presence could indicate a potential area of operational concern.

--- Agent: CloudSec Report ---
Personality: Observant, data-driven, likes patterns, focused on compliance.
Focus: Evaluates cloud resource usage, looks for compliance violations, and identifies anomalies within cloud services.
Frame: Frame 4: A person is running.
Analysis: The person running could be an anomaly, which could indicate a cloud service issue.

--- Agent: AISec Report ---
Personality: Curious, analytical, looks for trends, and hyperfocuses on things.
Focus: Monitors user behavior patterns, identifies anomalies in model usage, and detects potential adversarial attacks on AI systems.
Frame: Frame 7: A person is typing on a keyboard very fast.
Analysis: The fast typing could be indicative of some sort of threat.
Frame: Frame 10: A user is training an AI model.
Analysis: A user is training an AI model, that is something to be monitored.
Frame: Frame 11: An AI model is misidentifying people
Analysis: The AI model is having trouble and needs to be looked at.

--- Agent: Architect Report ---
Personality: Strategic, visionary, decisive, no-nonsense, frustrated with repetitive mistakes.
Focus: Identifies systemic weaknesses, enforces best practices, designs resilient systems, and pushes for architectural changes to prevent future incidents.
Frame: Frame 8: An old Windows screen with AD login prompt is shown.
Analysis: The AD login prompt is a major problem.
Frame: Frame 9: A new modern SAML login page is shown
Analysis: The new SAML login is good, and should be deployed.

--- Video Analysis Completed ---

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Future Enhancements

*   Integrate a real-time video feed.
*   Utilize image analysis alongside text analysis.
*   Implement true concurrency with threading or `asyncio`.
*   Create a UI for real-time output and reporting.
*   Connect agent outputs to SIEM or other security tools.

## Acknowledgments

*   This project was inspired by real-world security challenges, expressed by Eric M. https://www.linkedin.com/in/59852820r9f/

Code is meant for demonstration purposes only.  Not for production use.
