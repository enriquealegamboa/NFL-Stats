import type { ErrorRequestHandler } from "express";
import { AppError, ErrorCode, type ErrorEnvelope } from "../lib/errors.js";

export const errorHandler: ErrorRequestHandler = (err, req, res, _next) => {
  if (err instanceof AppError) {
    const body: ErrorEnvelope = {
      error: {
        code: err.code,
        message: err.message,
        ...(err.details !== undefined ? { details: err.details } : {}),
      },
    };
    res.status(err.status).json(body);
    return;
  }

  // Unknown error: log full detail server-side, return opaque 500.
  console.error("[unhandled]", {
    method: req.method,
    path: req.originalUrl,
    err,
  });

  const body: ErrorEnvelope = {
    error: {
      code: ErrorCode.INTERNAL_ERROR,
      message: "Internal server error",
    },
  };
  res.status(500).json(body);
};
