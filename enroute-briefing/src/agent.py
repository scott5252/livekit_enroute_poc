"""Entrypoint for the en route briefing agent.

This file only wires things together: it registers the agent with LiveKit and,
for each job, loads the visit, builds the session and starts the briefing. The
logic lives in the briefing package.
"""

import json
import logging
from dataclasses import replace

from dotenv import load_dotenv
from livekit.agents import AgentServer, JobContext, cli, room_io
from livekit.agents.voice.events import CloseEvent, ErrorEvent
from livekit.plugins import ai_coustics

from briefing.assistant import BriefingAgent
from briefing.config import AGENT_NAME, Settings, load_settings
from briefing.models import PayloadError, Visit
from briefing.payload import load_visit
from briefing.prompts import DELIVER_BRIEFING, EXPLAIN_NO_PAYLOAD
from briefing.sessions import build_session
from briefing.state import BriefingState

logger = logging.getLogger("agent")

# Read .env.local, then validate settings once. A bad value stops the agent at
# startup, where it is easy to see, and not in the middle of a briefing.
load_dotenv(".env.local")
SETTINGS = load_settings()

server = AgentServer()


def _visit_source(ctx: JobContext) -> tuple[str | None, Settings]:
    """Where this job's visit comes from: the dispatch metadata, in production.

    Under a simulation (lk agent simulate, scenarios.yaml) a scenario may carry the
    visit in its userdata as "visit", so every run of it briefs the same data. A
    null "visit" simulates a dispatch with no metadata, so the DEV_PAYLOAD_FILE
    fallback is switched off for that job. In production there is no simulation
    context and nothing here changes.
    """
    sim = ctx.simulation_context()
    if sim is None or "visit" not in sim.userdata():
        return ctx.job.metadata, SETTINGS
    visit = sim.userdata()["visit"]
    metadata = json.dumps(visit) if visit is not None else None
    return metadata, replace(SETTINGS, dev_payload_file=None)


@server.rtc_session(agent_name=AGENT_NAME)
async def entrypoint(ctx: JobContext):
    """Runs once per dispatch. One job = one room = one briefing."""
    # Every log line from this job carries the room name.
    ctx.log_context_fields = {"room": ctx.room.name}

    # 1. Load the visit. The server sent it as job metadata at dispatch.
    metadata, settings = _visit_source(ctx)
    visit: Visit | None
    try:
        visit = load_visit(metadata, settings)
    except PayloadError as err:
        # Do not crash: join anyway and tell the provider what happened.
        logger.error("could not load visit: %s", err)
        visit = None

    # Log ids only. Never log the payload: it contains patient information.
    logger.info(
        "starting briefing: visit=%s model=%s",
        visit.visit_id if visit else None,
        SETTINGS.briefing_model,
    )

    # 2. Build the session and attach handlers before anything can go wrong.
    session = build_session(SETTINGS, BriefingState(visit=visit))

    @session.on("error")
    def on_error(event: ErrorEvent) -> None:
        logger.error(
            "session error: source=%s error=%s",
            type(event.source).__name__,
            event.error,
        )

    @session.on("close")
    def on_close(event: CloseEvent) -> None:
        logger.info("session closed: reason=%s", event.reason)

    async def on_shutdown() -> None:
        logger.info("job finished: visit=%s", visit.visit_id if visit else None)

    ctx.add_shutdown_callback(on_shutdown)

    # 3. Start the session: this warms up the models and attaches to the room.
    await session.start(
        agent=BriefingAgent(visit),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=ai_coustics.audio_enhancement(
                    model=ai_coustics.EnhancerModel.QUAIL_VF_S
                ),
            ),
        ),
    )

    # 4. Join the room. From here the provider can hear the agent.
    await ctx.connect()

    # 5. Speak first: deliver the briefing without waiting to be asked.
    await session.generate_reply(
        instructions=DELIVER_BRIEFING if visit else EXPLAIN_NO_PAYLOAD
    )


if __name__ == "__main__":
    cli.run_app(server)
