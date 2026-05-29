import type { RequestHandler } from "express";
import { ZodError, type ZodTypeAny } from "zod";
import { ValidationError } from "../lib/errors.js";

type Source = "body" | "query" | "params";

export function validate(schema: ZodTypeAny, source: Source = "body"): RequestHandler {
  return (req, _res, next) => {
    const result = schema.safeParse(req[source]);
    if (!result.success) {
      next(toValidationError(result.error, source));
      return;
    }
    // Replace the source with the parsed (and possibly coerced) value.
    (req as unknown as Record<Source, unknown>)[source] = result.data;
    next();
  };
}

function toValidationError(err: ZodError, source: Source): ValidationError {
  const issues = err.issues.map((i) => ({
    path: [source, ...i.path.map(String)].join("."),
    message: i.message,
    code: i.code,
  }));
  return new ValidationError("Request validation failed", { issues });
}
