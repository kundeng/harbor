// Descriptor loader and validator (skeleton)
// Runs under Deno in a runner container.

export type Descriptor = {
  version: number;
  profiles?: Record<string, { services: string[]; options?: string[] }>;
  source?: unknown;
  prepare?: unknown;
  deploy?: unknown;
  post_deploy?: unknown;
  destroy?: unknown;
};

export async function loadDescriptor(path = "harbor2/etc/harbor.yaml"): Promise<Descriptor> {
  const text = await Deno.readTextFile(path);
  // naive YAML parse placeholder; replace with a safe YAML parser in M1
  // @ts-ignore - placeholder JSON if YAML already rendered
  try { return JSON.parse(text) as Descriptor; } catch {
    return { version: 1 } as Descriptor; // stub fallback
  }
}

export function validateDescriptor(_d: Descriptor): void {
  // TODO: implement schema validation (version, stages, known keys)
}
