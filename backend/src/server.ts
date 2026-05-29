import "dotenv/config";
import express from "express";
import cors from "cors";
import { healthRouter } from "./routes/health.js";
import { errorHandler } from "./middleware/errorHandler.js";

const app = express();

app.use(express.json());
app.use(
  cors({
    origin: process.env.CORS_ORIGIN?.split(",").map((s) => s.trim()) ?? "*",
  })
);

app.use("/health", healthRouter);

app.get("/", (_req, res) => {
  res.json({ name: "nfl-stats-backend", status: "ok" });
});

// Must be registered last, after all routes.
app.use(errorHandler);

const port = Number(process.env.PORT) || 8080;
app.listen(port, () => {
  console.log(`backend listening on :${port}`);
});
