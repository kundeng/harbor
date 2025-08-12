// Workflow runner (skeleton)
// Executes stages and actions described in harbor.yaml using runner semantics.

import { loadDescriptor, validateDescriptor } from "./descriptor.ts";

export async function run(stage: string, profile = "default"): Promise<void> {
  const d = await loadDescriptor();
  validateDescriptor(d);
  // TODO: resolve profile, then dispatch to stage executors
  switch (stage) {
    case "source":
      // await runSource(d, profile)
      break;
    case "prepare":
      // await runPrepare(d, profile)
      break;
    case "deploy":
      // await runDeploy(d, profile)
      break;
    default:
      throw new Error(`Unknown stage: ${stage}`);
  }
}
