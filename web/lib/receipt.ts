export type Severity = "critical" | "moderate" | "minor";
export type Verdict = "HONEST" | "MOSTLY HONEST" | "SNEAKY" | "LIAR";
export type Grade = "A" | "B" | "C" | "D" | "F";
export interface Flag { label: string; file: string; line: number | null; severity: Severity; evidence: string; }
export interface Receipt {
  pr: { repo: string; number: number; title: string; url: string; body?: string; author?: string | null };
  verdict: Verdict; grade: Grade;
  delivered: Flag[]; undisclosed: Flag[]; unhonored: Flag[];
  parsed_claims: string[]; math: string;
}
