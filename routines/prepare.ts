// Prepare stage (skeleton)
// Env layering + secrets + interpolation to var/run

export type EnvSource = { type: string; file?: string; dir?: string; pattern?: string; optional?: boolean };

export async function mergeEnv(_sources: EnvSource[]): Promise<Record<string, string>> {
  // TODO: implement layered merge; SOPS optional via AGE_PRIVATE_KEY
  return {};
}

export async function interpolateTemplates(_service: string, _env: Record<string, string>): Promise<void> {
  // TODO: envsubst + minimal handlebars-like rendering
}
