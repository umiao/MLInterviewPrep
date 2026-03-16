import { useMemo } from "react";
import { useSearchParams } from "react-router-dom";

/** Schema entry describing how to serialize/deserialize one filter param. */
interface ParamDef<T> {
  /** Default value when the param is absent from the URL. */
  defaultValue: T;
  /** Convert URL string to the typed value. Defaults to identity. */
  parse?: (raw: string) => T;
  /** Convert typed value to URL string. Defaults to String(). */
  serialize?: (value: T) => string;
}

/** A record mapping param names to their schema definitions. */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type ParamSchema = Record<string, ParamDef<any>>;

/** Infer the typed values from a schema. */
type ParamValues<S extends ParamSchema> = {
  [K in keyof S]: S[K]["defaultValue"];
};

/** Setters: one per param, plus a resetAll. */
type ParamSetters<S extends ParamSchema> = {
  [K in keyof S as `set${Capitalize<string & K>}`]: (
    value: S[K]["defaultValue"],
  ) => void;
} & {
  resetAll: () => void;
};

/**
 * Stores filter/sort state in URL search params via useSearchParams.
 *
 * Usage:
 * ```ts
 * const [values, { setDifficulty, setSortBy, resetAll }] = useFilterParams({
 *   difficulty: { defaultValue: undefined as string | undefined },
 *   sortBy:     { defaultValue: "created_at" },
 * });
 * ```
 *
 * - Params at their default value are omitted from the URL (clean URLs).
 * - Filters persist across navigation and browser back/forward.
 */
export function useFilterParams<S extends ParamSchema>(
  schema: S,
): [ParamValues<S>, ParamSetters<S>] {
  const [searchParams, setSearchParams] = useSearchParams();

  // Parse current URL into typed values
  const values = useMemo(() => {
    const result: Record<string, unknown> = {};
    for (const [key, def] of Object.entries(schema)) {
      const raw = searchParams.get(key);
      if (raw === null) {
        result[key] = def.defaultValue;
      } else {
        result[key] = def.parse ? def.parse(raw) : raw;
      }
    }
    return result as ParamValues<S>;
  }, [searchParams, schema]);

  // Build setters object
  const setters = useMemo(() => {
    const obj: Record<string, unknown> = {};

    for (const key of Object.keys(schema)) {
      const capitalised = key.charAt(0).toUpperCase() + key.slice(1);
      obj[`set${capitalised}`] = (value: unknown) => {
        setSearchParams(
          (prev) => {
            const next = new URLSearchParams(prev);
            const def = schema[key];
            const serialized = def.serialize
              ? def.serialize(value)
              : String(value ?? "");

            // Omit param if it matches default (keep URL clean)
            if (
              value === def.defaultValue ||
              value === undefined ||
              value === "" ||
              serialized === ""
            ) {
              next.delete(key);
            } else {
              next.set(key, serialized);
            }
            return next;
          },
          { replace: true },
        );
      };
    }

    obj.resetAll = () => {
      setSearchParams({}, { replace: true });
    };

    return obj as ParamSetters<S>;
    // setSearchParams is stable from react-router, schema is expected to be
    // defined at module level or memoized by the consumer.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [setSearchParams, schema]);

  return [values, setters];
}
