import { Router } from "express";
import { z } from "zod";
import { validate } from "../middleware/validate.js";

export const healthRouter = Router();

healthRouter.get("/", (_req, res) => {
  res.json({ status: "ok", uptime: process.uptime() });
});

// Smoke test for the validation + error envelope wiring.
// POST /health/echo { message: string (1..280) } -> { echoed: string }
const echoSchema = z.object({
  message: z.string().min(1).max(280),
});

healthRouter.post("/echo", validate(echoSchema), (req, res) => {
  const { message } = req.body as z.infer<typeof echoSchema>;
  res.json({ echoed: message });
});
