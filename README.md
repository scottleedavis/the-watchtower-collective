# The Watchtower Collective
WORK IN PROGRESS

This project demonstrates a multi-agent security system where specialized AI-powered agents collaborate to analyze a shared video stream, providing a comprehensive view of potential threats. This system leverages a Zoom live stream, processed by a Python server, and analyzed by individual agents using the Google Gemini API.

## Understanding the Setup

1.  **Zoom Live Stream:** You use the Zoom client live streaming feature to push its video and audio to your server's RTMP endpoint.
2.  **RTMP Server:** A Python server acts as a simple RTMP endpoint. It receives the video stream from Zoom using `ffmpeg`, and prepares the frames for distribution.
3.  **Agent Connections:** AI Agents connect to the server using WebRTC to receive the video frames.
4.  **Video Analysis:** Agents process the video stream frames and analyze them using the Google Gemini API, then share their observations.

## Description

The Watchtower Collective is a proof-of-concept project that simulates a security operations center (SOC). It uses multiple, specialized AI agents, each with a unique focus, to analyze a live video stream of various security tools. By providing layered analysis and multiple perspectives, this system aims to enhance threat detection and security awareness.

The system is designed to mimic a real-world scenario where multiple security professionals with different areas of expertise monitor various security tools. The agents act as a "threat-aware panel", collectively analyzing the stream to identify incidents and anomalies.

## Key Features

*   **Multi-Agent System:** Employs a team of collaborative AI agents to analyze a shared video stream.
*   **Specialized Agents:** Each agent simulates a different security role (SecOps, DevOps, CloudSec, AISec, Architect), focusing on specific areas.
*   **Real-Time Video Analysis:** Uses the `ffmpeg` library to grab the RTMP stream, and then converts the frames to be used for WebRTC.
*   **Gemini API Integration:** Agents use the Google Gemini API to analyze video frames, leveraging advanced natural language understanding.
*   **Modular Design:** Easily extensible to incorporate additional security agents or video analysis techniques.
*   **Real-time Output:** Reports the individual analysis of each agent, showcasing diverse perspectives.
*   **Zoom Live Stream Integration:** Integrates with Zoom live stream via RTMP, simulating real-world video feeds.

## Agents

The following security agents are included:

*   **SecOps:** Vigilant, focused on threats and vulnerabilities, detail-oriented, slightly cynical. Identifies potential security breaches, unusual activity patterns, and deviations from established policies.
*   **DevOps:** Practical, proactive, solution-oriented, loves automation, and impatient with slow processes. Looks for operational issues, performance bottlenecks, and potential system instabilities.
*   **CloudSec:** Observant, data-driven, likes patterns, focused on compliance. Evaluates cloud resource usage, looks for compliance violations, and identifies anomalies within cloud services.
*   **AISec:** Curious, analytical, looks for trends, and hyperfocuses on things. Monitors user behavior patterns, identifies anomalies in model usage, and detects potential adversarial attacks on AI systems.
*   **Architect:** Strategic, visionary, decisive, no-nonsense, frustrated with repetitive mistakes. Identifies systemic weaknesses, enforces best practices, designs resilient systems, and pushes for architectural changes to prevent future incidents.

## Getting Started

### Prerequisites

*   Python 3.6+
*   Google Gemini API Key (set as an environment variable: `GOOGLE_API_KEY`)
*   Zoom Account
*   Zoom Client installed on your operating system.
*   `ffmpeg` command line tool
*   `google-generativeai` library

### Installation

1.  Clone the repository:

    ```bash
    git clone https://github.com/scottleedavis/the-watchtower-collective.git
    cd the-watchtower-collective
    ```
2.  Create a Python virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
3.  Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

1.  **Set your `GOOGLE_API_KEY` environment variable:**

    ```bash
    export GOOGLE_API_KEY="YOUR_API_KEY"
    ```

    (or configure it in an `.env` file)

2.  **Configure Zoom Live Streaming:**
     - In Zoom, navigate to *Settings* > *In Meeting (Advanced)* > Enable *Allow live streaming the meetings*.
     - In your Zoom meeting, click *More* > *Live on Custom Live Streaming Service*.
     - Set the *Stream URL* to `rtmp://<url_to_app>:1935/live/stream` (or whatever rtmp endpoint you have set up.)
     - Set the *Stream Key* to `secret!` (or any stream key, but you do not need one if you are only running locally).

### Usage

1.  Start the server, and the agents in split-screen mode (using `tmux`):
    ```bash
    ./start_watchtower.sh
    ```
    This command runs `app.py` in the left pane and three `agent.py` in the other panes.
2. **Start the Stream:** Start streaming in Zoom. The agents will connect to the stream, and provide their analysis.


## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under Apache 2.0  - see the [LICENSE](LICENSE) file for details.

## Future Enhancements

*   Expand the number of agent types.
*   Integrate a UI for real-time agent output and video display.
*   Connect agent output to SIEM or other security tools.
*   Implement improved video analysis techniques with better models.
*   Add agent-to-agent communication (i.e. allowing agents to respond to each other).

## Acknowledgments

* This project was inspired by [SOC stories](https://www.linkedin.com/in/59852820r9f/)
* Kudos to [KnugiHK/rtmplite3](https://github.com/KnugiHK/rtmplite3) for a python rtmp server
* This is meant for demonstration purposes only. Not for production use. Use with caution.
