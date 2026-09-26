const BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function handle(res) {
  if (!res.ok) {
    let body = {};
    try {
      body = await res.json();
    } catch {
      body = { detail: res.statusText };
    }
    const err = new Error(body.detail || JSON.stringify(body));
    err.body = body;
    err.status = res.status;
    throw err;
  }
  return res.json();
}

export async function createRun(topic) {
  const res = await fetch(`${BASE}/api/runs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ topic }),
  });
  return handle(res);
}

export async function getRun(id) {
  const res = await fetch(`${BASE}/api/runs/${id}`);
  return handle(res);
}
