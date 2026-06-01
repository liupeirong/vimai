# Progress Log

> Append session logs conforming to this TypeScript schema:
interface session_log {
    datetime: string; // session start datetime YYYY-MM-DD HH-mm
    what_was_done: string[]; // features/tests implemented, bugs fixed etc
    decision: string[]; // what decisions were made, changed
    issues: string[]; // what issues were encountered, what's their status now
    benchmark_results?: Record<string, string>; // performance benchmark numbers if any, ex. {Query_What_is_the_architecture: "~250ms with 2 citations"}
    next_step: string;
}[]
