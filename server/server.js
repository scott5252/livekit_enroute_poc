// server.js - POC server. Launches the briefing agent with a mock visit.
// All data comes from mock-visits.json. No real backend system is contacted.
import { randomUUID } from 'node:crypto';
import { readFileSync } from 'node:fs';
import dotenv from 'dotenv';
import express from 'express';
import { AccessToken, AgentDispatchClient } from 'livekit-server-sdk';

// Load LIVEKIT_URL, LIVEKIT_API_KEY and LIVEKIT_API_SECRET from .env.local
dotenv.config({ path: '.env.local' });

const { LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET } = process.env;
const AGENT_NAME = process.env.AGENT_NAME ?? 'enroute-briefing';
const AGENT_DEPLOYMENT = process.env.AGENT_DEPLOYMENT ?? 'local';
const PORT = Number(process.env.PORT ?? 3000);

// Which visit in mock-visits.json to brief. visit-1002 is Margaret Ellis.
const VISIT_ID = process.env.VISIT_ID ?? 'visit-1002';

if (!LIVEKIT_URL || !LIVEKIT_API_KEY || !LIVEKIT_API_SECRET) {
  console.error('Missing LIVEKIT_URL, LIVEKIT_API_KEY or LIVEKIT_API_SECRET.');
  console.error('Check the .env.local file in the server folder.');
  process.exit(1);
}

// Read the mock file on every request, so edits show up without a restart.
function loadVisits() {
  return JSON.parse(readFileSync('mock-visits.json', 'utf8'));
}

const dispatchClient = new AgentDispatchClient(
  LIVEKIT_URL,
  LIVEKIT_API_KEY,
  LIVEKIT_API_SECRET,
);

const app = express();
app.use(express.json());

// "Launch agent": send the mock visit to the agent and return a token.
app.post('/api/briefing-session', async (_req, res) => {
  const visit = loadVisits().find((v) => v.visit_id === VISIT_ID);
  if (!visit) {
    res.status(404).json({ error: `No visit ${VISIT_ID} in mock-visits.json` });
    return;
  }

  // A new room for every briefing.
  const roomName = `brief-${randomUUID()}`;

  try {
    // Dispatch the agent into the room with the visit as its job metadata.
    const options = { metadata: JSON.stringify(visit) };
    if (AGENT_DEPLOYMENT && AGENT_DEPLOYMENT !== 'production') {
      options.deployment = AGENT_DEPLOYMENT;
    }
    await dispatchClient.createDispatch(roomName, AGENT_NAME, options);

    // Create the access token that lets the browser join the same room.
    const token = new AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET, {
      identity: `provider-${randomUUID().slice(0, 8)}`,
      name: 'Service provider',
      ttl: '10m',
    });
    token.addGrant({
      roomJoin: true,
      room: roomName,
      canPublish: true,
      canSubscribe: true,
    });

    console.log(`briefing: visit=${VISIT_ID} room=${roomName} agent=${AGENT_NAME}`);

    res.status(201).json({
      server_url: LIVEKIT_URL,
      participant_token: await token.toJwt(),
    });
  } catch (err) {
    console.error('Could not start the briefing:', err);
    res.status(502).json({ error: 'Could not reach LiveKit to start the briefing' });
  }
});

app.listen(PORT, () => {
  const deployment = AGENT_DEPLOYMENT || 'production';
  console.log(`Server listening on http://localhost:${PORT}`);
  console.log(`Dispatching agent "${AGENT_NAME}" on deployment "${deployment}"`);
  console.log(`Mock visit: ${VISIT_ID}`);
});
