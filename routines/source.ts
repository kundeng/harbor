// Source stage executor (skeleton)
// Mirrors compose_with_options() rules to produce ordered -f files and resolved services/options.

export type SourceOutput = { files: string[]; services: string[]; options: string[] };

export async function executeSource(_profile = "default"): Promise<SourceOutput> {
  // TODO: detect capabilities (nvidia, cdi, rocm, mdc)
  // TODO: include base compose.yml and overlays per rules
  return { files: ["compose.yml"], services: [], options: ["*"] };
}
